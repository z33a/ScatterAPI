# External imports
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

# Internal imports
from database import engine
from tags.models import Tags, TagCreate, TagResponse, TagCollectionLinks, TagUploadLinks
from scatter_collections.models import CollectionResponse, Collections
from uploads.models import Uploads, UploadResponse
from users.utils import verify_authenticated_user
from users.models import UserResponse
from config import ANONYMOUS_USER

tags_router = APIRouter()

@tags_router.post("/tags", tags=["tags"], response_model=TagResponse)
async def new_tag(new_tag: TagCreate, current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create new tag as anonymous user!")

    with Session(engine) as session:
        statement = select(Tags).where(Tags.name == new_tag.name)
        results = session.exec(statement)
        tag = results.first()

        if tag is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag with the same name already exists!")
    
    new_tag = Tags(**new_tag.dict(), created_by=current_user.id)

    with Session(engine) as session:
        db_tag = Tags.model_validate(new_tag)
        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)
        new_tag = db_tag

    return new_tag

@tags_router.get("/tags", tags=["tags"], response_model=list[TagResponse])
async def get_all_tags():
    with Session(engine) as session:
        statement = select(Tags).where(Tags.deleted_at == None)
        results = session.exec(statement)
        return results.all()

@tags_router.get("/tags/{tag_id}", tags=["tags"], response_model=TagResponse)
async def get_tag(tag_id: int):
    with Session(engine) as session:
        statement = select(Tags).where(Tags.id == tag_id)
        results = session.exec(statement)
        tag = results.first()

        if tag is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found!")
                
        return tag

@tags_router.get("/tags/{tag_id}/collections", tags=["tags"], response_model=list[CollectionResponse])
async def get_all_collections_with_tag(tag_id: int):
    collections = []

    with Session(engine) as session:
        statement = select(TagCollectionLinks).where(TagCollectionLinks.tag_id == tag_id)
        results = session.exec(statement)
        
        for tag_collection_link in results.all():
            statement = select(Collections).where(Collections.id == tag_collection_link.collection_id)
            results1 = session.exec(statement)
            collections.append(results1.first())

    return collections

@tags_router.get("/tags/{tag_id}/uploads", tags=["tags"], response_model=list[UploadResponse])
async def get_all_uploads_with_tag(tag_id: int):
    uploads = []

    with Session(engine) as session:
        statement = select(TagUploadLinks).where(TagUploadLinks.tag_id == tag_id)
        results = session.exec(statement)
        
        for tag_upload_link in results.all():
            statement = select(Uploads).where(Uploads.id == tag_upload_link.upload_id)
            results1 = session.exec(statement)
            uploads.append(results1.first())

    return uploads