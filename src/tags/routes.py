# External imports
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

# Internal imports
from database import engine
from tags.models import Tags, TagCreate, TagResponse
from users.utils import verify_authenticated_user
from users.models import UserResponse

tags_router = APIRouter()

@tags_router.post("/tags", tags=["tags"], response_model=TagResponse)
async def new_tag(new_tag: TagCreate, current_user: UserResponse = Depends(verify_authenticated_user)):
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