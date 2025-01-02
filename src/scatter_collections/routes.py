# External imports
from fastapi import APIRouter, HTTPException, Depends, Form, status
from sqlmodel import Session, select

# Internal imports
from database import engine
from scatter_collections.models import Collections, CollectionCreate, CollectionResponse, UploadCollectionLink
from users.utils import verify_authenticated_user
from users.models import UserResponse
from config import ANONYMOUS_USER
from scatter_collections.types import CollectionPrivacy

collections_router = APIRouter()

@collections_router.post("/collections", tags=["collections"], response_model=CollectionResponse)
async def new_collection(title: str = Form(), description: str | None = Form(default=None), privacy: CollectionPrivacy = Form(), current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER and privacy == CollectionPrivacy.PRIVATE: # Creating private collection is not allowed as anonymous user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creating private collection is not allowed as anonymous user!")

    with Session(engine) as session:
        statement = select(Collections).where(Collections.title == title)
        results = session.exec(statement)
        collection = results.first()

        if collection is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection with the same title already exists!")

    # Create inital collection database entry
    new_collection = Collections(title=title, description=description, privacy=privacy, created_by=current_user.id)
    
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

@collections_router.post("/collections/{collection_id}/uploads", tags=["collections"], response_model=UploadCollectionLink)
async def add_upload_to_collection(collection_id: int, upload_id: int = Form(), current_user: UserResponse = Depends(verify_authenticated_user)):
    collection = None

    with Session(engine) as session:
        statement = select(Collections).where(Collections.id == collection_id)
        results = session.exec(statement)
        db_collection = results.first()

        if db_collection is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found!")
        else:
            collection = db_collection

    if current_user.id != collection.created_by and collection.privacy == CollectionPrivacy.PRIVATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add uploads to private collection!")

    upload_collection_link = UploadCollectionLink(upload_id=upload_id, collection_id=collection_id, created_by=current_user.id)

    with Session(engine) as session:
        db_upload_collection_link = UploadCollectionLink.model_validate(upload_collection_link)
        session.add(db_upload_collection_link)
        session.commit()
        session.refresh(db_upload_collection_link)
        upload_collection_link = db_upload_collection_link

    return upload_collection_link

@collections_router.get("/collections/{collection_id}/uploads", tags=["collections"], response_model=list[UploadCollectionLink])
async def get_all_uploads_in_collection(collection_id: int):
    with Session(engine) as session:
        statement = select(UploadCollectionLink).where(UploadCollectionLink.collection_id == collection_id)
        results = session.exec(statement)
        return results.all()