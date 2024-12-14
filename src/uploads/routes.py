# External imports
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
import os
from collections import Counter
from sqlmodel import Session, select
from fastapi.responses import FileResponse

# Internal imports
from uploads.models import Uploads, UploadResponse, UploadCreate
from users.models import UserResponse
from users.utils import verify_authenticated_user
from config import MAX_FILE_SIZE, UPLOAD_DIR
from files.utils import stream_save_file, create_file, generate_filename
from files.models import FileResponseSQL
from uploads.types import UploadTypes
from database import engine

uploads_router = APIRouter()

@uploads_router.post("/uploads", tags=["uploads"], response_model=UploadResponse)
async def new_upload(files: list[UploadFile], thumbnail: UploadFile | None = None, title: str = Form(), description: str | None = Form(default=None), current_user: UserResponse = Depends(verify_authenticated_user)):
    with Session(engine) as session:
        statement = select(Uploads).where(Uploads.title == title)
        results = session.exec(statement)
        upload = results.first()

        if upload is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Upload with the same title already exists!")

    # Extract the primary MIME type (the part before the slash)
    primary_mimes = [file.content_type.split('/')[0] for file in files]
    
    # Count the occurrences of each primary MIME type
    primary_mime_counts = Counter(primary_mimes)
    
    # Get the most common primary MIME type
    most_common_mime = primary_mime_counts.most_common(1)[0][0]
    
    # Create inital upload database entry
    new_upload = Uploads(title=title, description=description, type=most_common_mime, created_by=current_user.id)
    
    with Session(engine) as session:
        db_upload = Uploads.model_validate(new_upload)
        session.add(db_upload)
        session.commit()
        session.refresh(db_upload)
        new_upload = db_upload

    thumbnail_location = None

    # Get thumbnail
    if thumbnail is not None:
        thumbnail_location = os.path.join(str(current_user.id), str(new_upload.id), f"thumbnail{os.path.splitext(thumbnail.filename)[1]}")
        file_size: int = await stream_save_file(file=thumbnail, target=os.path.join(UPLOAD_DIR, thumbnail_location), max_size=MAX_FILE_SIZE)
    else:
        for file in files:
            if file.content_type.split('/')[0] == "image":
                thumbnail_location = os.path.join(str(current_user.id), str(new_upload.id), f"thumbnail{os.path.splitext(file.filename)[1]}")
                file_size: int = await stream_save_file(file=file, target=os.path.join(UPLOAD_DIR, thumbnail_location), max_size=MAX_FILE_SIZE)
                break
        
    if thumbnail_location is not None:
        with Session(engine) as session:
            statement = select(Uploads).where(Uploads.id == new_upload.id)
            results = session.exec(statement)
            upload = results.one()

            upload.thumbnail_location = thumbnail_location
            session.add(upload)
            session.commit()
            session.refresh(upload)
            new_upload = upload

    # Save all the files
    for file in files:
        generated_filename = generate_filename()
        _, file_ext = os.path.splitext(file.filename)
        file_location = os.path.join(str(current_user.id), str(new_upload.id), "files")
        file_size: int = await stream_save_file(file=file, target=os.path.join(UPLOAD_DIR, file_location, f"{generated_filename}{file_ext}"), max_size=MAX_FILE_SIZE)
        saved_file: FileResponseSQL = create_file(file=file, upload_id=new_upload.id, file_location=file_location, file_size=file_size, created_by=current_user.id, generated_filename=generated_filename)

    return new_upload    

@uploads_router.get("/uploads", tags=["uploads"], response_model=list[UploadResponse])
async def get_all_uploads(offset: int = 0, limit: int | None = 100, created_before: int | None = None, created_after: int | None = None, created_by: int | None = None):
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
        upload = results.first()

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
        upload = results.first()

        if upload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
        
        file_path = os.path.join(UPLOAD_DIR, upload.thumbnail_location)

        if os.path.exists(file_path):
            return file_path
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found!")