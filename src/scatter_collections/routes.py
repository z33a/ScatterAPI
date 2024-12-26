# External imports
from fastapi import APIRouter, HTTPException, Depends, Form, status
from sqlmodel import Session, select

# Internal imports
from collections.models import Collections, CollectionCreate, CollectionResponse
from users.utils import verify_authenticated_user
from users.models import UserResponse
from config import ANONYMOUS_USER
from collections.types import CollectionPrivacy

collections_router = APIRouter()

@collections_router.post("/collections", tags=["collections"], response_model=CollectionResponse)
async def new_collection(title: str = Form(), description: str | None = Form(default=None), privacy: CollectionPrivacy = Form(), current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER and new_collection.privacy == CollectionPrivacy.PRIVATE.value: # Creating private collection is not allowed as anonymous user
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