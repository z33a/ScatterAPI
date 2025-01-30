# External imports
from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlmodel import Session, select

# Internal imports
from database import engine
from scatter_collections.models import Collections, CollectionCreate, CollectionResponse, UploadCollectionLinks
from tags.models import TagCollectionLinks, Tags
from uploads.models import Uploads, UploadResponse
from users.utils import verify_authenticated_user
from users.models import UserResponse
from config import ANONYMOUS_USER
from scatter_collections.types import CollectionPrivacy

collections_router = APIRouter()

@collections_router.post("/collections", tags=["collections"], response_model=CollectionResponse)
async def new_collection(new_collection: CollectionCreate, current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER and new_collection.privacy == CollectionPrivacy.PRIVATE: # Creating private collection is not allowed as anonymous user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creating private collection is not allowed as anonymous user!")

    with Session(engine) as session:
        statement = select(Collections).where(Collections.title == new_collection.title)
        results = session.exec(statement)
        collection = results.first()

        if collection is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection with the same title already exists!")

    # Create collection database entry
    new_collection = Collections(**new_collection.dict(), created_by=current_user.id)
    
    with Session(engine) as session:
        db_collection = Collections.model_validate(new_collection)
        session.add(db_collection)
        session.commit()
        session.refresh(db_collection)
        new_collection = db_collection

    return new_collection

@collections_router.get("/collections", tags=["collections"], response_model=list[CollectionResponse])
async def get_all_collections():
    with Session(engine) as session:
        statement = select(Collections).where(Collections.deleted_at == None)
        results = session.exec(statement)
        return results.all()

@collections_router.get("/collections/{collection_id}", tags=["collections"], response_model=CollectionResponse)
async def get_collection(collection_id: int):
    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        collection = results.first()

        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
                
        return collection

@collections_router.post("/collections/{collection_id}/uploads", tags=["collections"], response_model=list[UploadCollectionLinks])
async def add_uploads_to_collection(collection_id: int, upload_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_collection = None

    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        collection = results.first()

        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
        else:
            current_collection = collection

    if current_user.id != current_collection.created_by and current_collection.privacy == CollectionPrivacy.PRIVATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add uploads to private collection!")

    links = []

    for upload_id in upload_ids:
        with Session(engine) as session:
            statement = select(Uploads).where(Uploads.id == upload_id)
            results = session.exec(statement)
            upload = results.first()

            if upload is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Upload {upload_id} not found!")

        with Session(engine) as session:
            statement = select(UploadCollectionLinks).where(UploadCollectionLinks.upload_id == upload_id, UploadCollectionLinks.collection_id == current_collection.id)
            results = session.exec(statement)
            upload_collection_link = results.first()

            if upload_collection_link is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Upload {upload_id} already added to collection {current_collection.id}!")

    for upload_id in upload_ids:
        upload_collection_link = UploadCollectionLinks(upload_id=upload_id, collection_id=collection_id, created_by=current_user.id)

        with Session(engine) as session:
            db_upload_collection_link = UploadCollectionLinks.model_validate(upload_collection_link)
            session.add(db_upload_collection_link)
            session.commit()
            session.refresh(db_upload_collection_link)
            upload_collection_link = db_upload_collection_link

        links.append(upload_collection_link)

    return links

@collections_router.delete("/collections/{collection_id}/uploads", tags=["collections"], response_model=bool)
async def remove_uploads_from_collection(collection_id: int, upload_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_collection = None

    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        collection = results.first()

        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
        else:
            current_collection = collection

    if current_user.id != current_collection.created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can remove uploads from collection! (Private or Public)")

    for upload_id in upload_ids:
        with Session(engine) as session:
            statement = select(UploadCollectionLinks).where(UploadCollectionLinks.upload_id == upload_id, UploadCollectionLinks.collection_id == current_collection.id)
            results = session.exec(statement)
            upload_collection_link = results.first()

            if upload_collection_link is not None:
                session.delete(upload_collection_link)
                session.commit()

    return True

@collections_router.get("/collections/{collection_id}/uploads", tags=["collections"], response_model=list[UploadResponse])
async def get_all_uploads_in_collection(collection_id: int):
    uploads = []

    with Session(engine) as session:
        statement = select(UploadCollectionLinks).where(UploadCollectionLinks.collection_id == collection_id)
        results = session.exec(statement)

        for upload_collection_link in results.all():
            statement = select(Uploads).where(Uploads.id == upload_collection_link.upload_id)
            results1 = session.exec(statement)
            uploads.append(results1.first())

    return uploads

@collections_router.post("/collections/{collection_id}/tags", tags=["collections"], response_model=list[TagCollectionLinks])
async def add_tags_to_collection(collection_id: int, tag_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_collection = None

    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        collection = results.first()

        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
        else:
            current_collection = collection

    if current_user.id != current_collection.created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add tags to collection! (Private or Public)")

    links = []

    for tag_id in tag_ids:
        with Session(engine) as session:
            statement = select(Tags).where(Tags.id == tag_id)
            results = session.exec(statement)
            tag = results.first()

            if tag is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {tag_id} not found!")

        with Session(engine) as session:
            statement = select(TagCollectionLinks).where(TagCollectionLinks.tag_id == tag_id, TagCollectionLinks.collection_id == current_collection.id)
            results = session.exec(statement)
            tag_collection_link = results.first()

            if tag_collection_link is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tag {tag_id} already added to collection {current_collection.id}!")

    for tag_id in tag_ids:
        tag_collection_link = TagCollectionLinks(tag_id=tag_id, collection_id=current_collection.id, created_by=current_user.id)

        with Session(engine) as session:
            db_tag_collection_link = TagCollectionLinks.model_validate(tag_collection_link)
            session.add(db_tag_collection_link)
            session.commit()
            session.refresh(db_tag_collection_link)
            tag_collection_link = db_tag_collection_link

        links.append(tag_collection_link)

    return links

@collections_router.delete("/collections/{collection_id}/tags", tags=["collections"], response_model=bool)
async def remove_tags_from_collection(collection_id: int, tag_ids: list[int] = Body(embed=True), current_user: UserResponse = Depends(verify_authenticated_user)):
    current_collection = None

    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        collection = results.first()

        if collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
        else:
            current_collection = collection

    if current_user.id != current_collection.created_by:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can remove tags from collection! (Private or Public)")

    for tag_id in tag_ids:
        with Session(engine) as session:
            statement = select(TagCollectionLinks).where(TagCollectionLinks.tag_id == tag_id, TagCollectionLinks.collection_id == current_collection.id)
            results = session.exec(statement)
            tag_collection_link = results.first()

            if tag_collection_link is not None:
                session.delete(tag_collection_link)
                session.commit()

    return True

@collections_router.get("/collections/{collection_id}/tags", tags=["collections"], response_model=list[TagCollectionLinks])
async def get_all_tags_of_collection(collection_id: int):
    with Session(engine) as session:
        statement = select(TagCollectionLinks).where(TagCollectionLinks.collection_id == collection_id)
        results = session.exec(statement)
        return results.all()