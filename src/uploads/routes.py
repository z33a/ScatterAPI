# External imports
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, status, Body
import os
from collections import Counter
from sqlmodel import Session, select, desc, asc, text
from fastapi.responses import FileResponse
import json
from jsonschema import validate, ValidationError
from io import BytesIO

# Internal imports
from uploads.models import Uploads, UploadResponse
from users.models import UserResponse
from users.utils import verify_authenticated_user
from files.utils import create_file, save_file
from uploads.types import OrderByTypes, OrderByDirectionTypes, order_by_metadata
from database import engine
from uploads.metadata_schemas import MetadataTypes, metadata_schemas
from uploads.utils import create_upload_thumbnail
from config import SAVE_DIR
from tags.models import Tags, TagUploadLinks

uploads_router = APIRouter()

@uploads_router.post("/uploads", tags=["uploads"], response_model=UploadResponse)
async def new_upload(
    files: list[UploadFile],
    thumbnail: UploadFile | None = None,
    metadata_type: MetadataTypes | None = Form(default=None),
    metadata_json: str | None = Form(default=None),
    title: str = Form(),
    description: str | None = Form(default=None),
    current_user: UserResponse = Depends(verify_authenticated_user)):

    if (metadata_type is None) != (metadata_json is None): # Same as (metadata_type is None and metadata_json is not None) or (metadata_type is not None and metadata_json is None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="When uploading metadata, define both 'metadata_type' and 'metadata_json'! If not uploading metadata do not define either of them!")

    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.title == title)
        results = session.exec(statement)
        upload = results.first()

        if upload is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Upload with the same title already exists!")

    # Process metadata
    if metadata_type is not None:
        try:
            metadata_json_parsed = json.loads(metadata_json)

            if metadata_type != MetadataTypes.OTHER: # If "other", skip validation and accept any JSON structure
                metadata_schema = metadata_schemas.get(metadata_type)

                if not metadata_schema:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid metadata type!")

                validate(instance=metadata_json_parsed, schema=metadata_schema) # If validation fails, a ValidationError will be raised
                metadata_json_validated = metadata_json_parsed
            else:
                metadata_json_validated = metadata_json_parsed
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {e}")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")
    else:
        metadata_json_validated = None

    # Get the most common primary mime type
    primary_mimes = [file.content_type.split('/')[0] for file in files]
    primary_mime_counts = Counter(primary_mimes)
    most_common_mime = primary_mime_counts.most_common(1)[0][0]

    # Create upload database entry
    new_upload = Uploads(title=title, description=description, type=most_common_mime, metadata_type=metadata_type, metadata_json=metadata_json_validated, created_by=current_user.id)
    
    with Session(engine) as session:
        db_upload = Uploads.model_validate(new_upload)
        session.add(db_upload)
        session.commit()
        session.refresh(db_upload)
        new_upload = db_upload

    # Save all the files
    for index, file in enumerate(files):
        await create_file(file=file, upload_id=new_upload.id, filename=str(index), created_by=current_user.id)

    # Generate thumbnail
    if thumbnail is not None:
        create_upload_thumbnail(file=thumbnail, upload_id=new_upload.id, is_user_uploaded=True)
    else:
        for file in files:
            await file.seek(0) # Always seek to 0 before reading a file
            generation_success = create_upload_thumbnail(file=file, upload_id=new_upload.id)

            if generation_success:
                break

    # Save backup metadata
    if metadata_json_validated is not None:
        json_data = json.dumps(metadata_json_validated, indent=4).encode('utf-8') # Convert the dictionary to a JSON string and then to bytes

        save_file(file_path=os.path.join(SAVE_DIR, "uploads", str(new_upload.id), "metadata.json"), data=json_data)

    return new_upload

@uploads_router.get("/uploads", tags=["uploads"], response_model=list[UploadResponse])
async def get_all_uploads(offset: int = 0, limit: int | None = None, created_before: int | None = None, created_after: int | None = None, created_by: int | None = None, filter_by_metadata_type: MetadataTypes | None = None, order_by: str | None = None, order_by_direction: OrderByDirectionTypes = OrderByDirectionTypes.DESC):
    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.deleted_at == None)

        # All optional query params - will combine using AND into one statement        
        if created_after is not None and created_before is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query 'created_before' and 'created_after' cannot be declared together!")

        if created_before is not None and created_after is None:
            statement = statement.where(Uploads.created_at < created_before)

        if created_after is not None and created_before is None:
            statement = statement.where(Uploads.created_at > created_after)

        if created_by is not None:
            statement = statement.where(Uploads.created_by == created_by)

        if filter_by_metadata_type is not None:
            statement = statement.where(Uploads.metadata_type == filter_by_metadata_type)

        if order_by is not None:
            if order_by in OrderByTypes:
                if order_by_direction == OrderByDirectionTypes.ASC:
                    statement = statement.order_by(asc(getattr(Uploads, order_by)))
                elif order_by_direction == OrderByDirectionTypes.DESC:
                    statement = statement.order_by(desc(getattr(Uploads, order_by)))
            else:
                if filter_by_metadata_type is not None: # Cannot sort by metadata while other metadata types are present
                    order_by_options = order_by_metadata.get(filter_by_metadata_type)

                    if order_by in order_by_options:
                        if order_by_direction == OrderByDirectionTypes.ASC:
                            statement = statement.order_by(asc(text(f"metadata_json->>'{order_by}'")))
                        elif order_by_direction == OrderByDirectionTypes.DESC:
                            statement = statement.order_by(desc(text(f"metadata_json->>'{order_by}'")))
                    else:
                        raise HTTPException()
                else:
                    raise HTTPException()

        if limit is not None:
            statement = statement.limit(limit)
            
        statement = statement.offset(offset)

        results = session.exec(statement)

        return results.all()

@uploads_router.get("/uploads/{upload_id}", tags=["uploads"], response_model=UploadResponse)
async def get_upload(upload_id: int):
    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.id == upload_id)
        results = session.exec(statement)
        upload = results.one()

        if upload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
                
        return upload

@uploads_router.put("/uploads/{upload_id}", tags=["uploads"])
async def update_upload(upload_id: int):
    pass

@uploads_router.get("/uploads/{upload_id}/thumbnail", tags=["uploads"], response_class=FileResponse)
async def get_upload_thumbnail(upload_id: int):
    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.id == upload_id)
        results = session.exec(statement)
        upload = results.one()

        if upload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
        
        file_path = os.path.join(SAVE_DIR, "uploads", str(upload.id), "thumbnail.jpg")

        if os.path.exists(file_path):
            return file_path
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found!")

@uploads_router.post("/uploads/{upload_id}/tags", tags=["uploads"], response_model=list[TagUploadLinks])
async def add_tags_to_upload(upload_id: int, tag_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_upload = None

    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.id == upload_id)
        results = session.exec(statement)
        upload = results.first()

        if upload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
        else:
            current_upload = upload

    if current_user.id != current_upload.created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add tags to upload!")

    links = []

    for tag_id in tag_ids:
        with Session(engine) as session:
            statement = select(Tags).where(Tags.id == tag_id)
            results = session.exec(statement)
            tag = results.first()

            if tag is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {tag_id} not found!")

        with Session(engine) as session:
            statement = select(TagUploadLinks).where(TagUploadLinks.tag_id == tag_id, TagUploadLinks.upload_id == current_upload.id)
            results = session.exec(statement)
            tag_upload_link = results.first()

            if tag_upload_link is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tag {tag_id} already added to upload {current_upload.id}!")

    for tag_id in tag_ids:
        tag_upload_link = TagUploadLinks(tag_id=tag_id, upload_id=current_upload.id, created_by=current_user.id)

        with Session(engine) as session:
            db_tag_upload_link = TagUploadLinks.model_validate(tag_upload_link)
            session.add(db_tag_upload_link)
            session.commit()
            session.refresh(db_tag_upload_link)
            tag_upload_link = db_tag_upload_link

        links.append(tag_upload_link)

    return links

@uploads_router.delete("/uploads/{upload_id}/tags", tags=["uploads"], response_model=bool)
async def remove_tags_from_upload(upload_id: int, tag_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_upload = None

    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.id == upload_id)
        results = session.exec(statement)
        upload = results.first()

        if upload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
        else:
            current_upload = upload

    if current_user.id != current_upload.created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can remove tags from upload!")

    for tag_id in tag_ids:
        with Session(engine) as session:
            statement = select(TagUploadLinks).where(TagUploadLinks.tag_id == tag_id, TagUploadLinks.upload_id == current_upload.id)
            results = session.exec(statement)
            tag_upload_link = results.first()

            if tag_upload_link is not None:
                session.delete(tag_upload_link)
                session.commit()

    return True

@uploads_router.get("/uploads/{upload_id}/tags", tags=["uploads"], response_model=list[TagUploadLinks])
async def get_all_tags_of_upload(upload_id: int):
    with Session(engine) as session:
        statement = select(TagUploadLinks).where(TagUploadLinks.upload_id == upload_id)
        results = session.exec(statement)
        return results.all()