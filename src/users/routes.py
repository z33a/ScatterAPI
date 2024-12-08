# External imports
from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlmodel import Session, select, or_
import datetime

# Internal imports
from users.models import Users, UserCreate, UserResponse, UserDeletionResponse
from database import engine
from auth.utils import hash_password
from users.utils import check_password_structure, verify_authenticated_user
from config import ANONYMOUS_USER
from users.types import UserStatuses

users_router = APIRouter()

# Sign up and create a new user
@users_router.post("/users", tags=["users"], response_model=UserResponse)
async def new_user(new_user: UserCreate):
    with Session(engine) as session:
        statement = select(Users).where(or_(Users.username == new_user.username, Users.email == new_user.email))
        results = session.exec(statement)

        if results.first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this username or email already exists!")

    if check_password_structure(new_user.password):
        hashed_password = hash_password(new_user.password)
        new_user.password = hashed_password

        with Session(engine) as session:
            db_user = Users.model_validate(new_user)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password! Must contain at least one uppercase letter, one lowercase letter, one digit, and one special symbol.")

# Get all users
@users_router.get("/users", tags=["users"], response_model=list[UserResponse])
async def get_all_users():
    with Session(engine) as session:
        statement = select(Users).where(Users.status != UserStatuses.DELETED.value)
        results = session.exec(statement)

        return results.all()

# Get a user logged in by the token !!! Must be before '/users/{user_id}' endpoint !!!
@users_router.get("/users/me", tags=["users"], response_model=UserResponse)
async def get_authenticated_user(current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER: # Login of anonymous user is not allowed in this endpoint
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authentication token provided!")

    return current_user

# Update a user logged in by the token
@users_router.put("/users/me", tags=["users"])
async def update_authenticated_user(current_user: UserResponse = Depends(verify_authenticated_user)):
    pass

# Delete a user logged in by the token
@users_router.delete("/users/me", tags=["users"], response_model=UserDeletionResponse)
async def delete_authenticated_user(user_to_delete: str = Form(...), current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER: # Login of anonymous user is not allowed in this endpoint
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authentication token provided!")

    with Session(engine) as session:
        statement = select(Users).where(Users.id == current_user.id)
        results = session.exec(statement)
        user = results.first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        elif user.username != user_to_delete:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username to delete and logged in user do not match!")

        user.status = UserStatuses.DELETED.value
        user.deleted_at = datetime.datetime.now(datetime.UTC).timestamp()

        session.add(user)
        session.commit()
        session.refresh(user)

    return UserDeletionResponse(
        message = f"User '{user.username}' with id {user.id} was successfully deleted.",
        disclaimer = "This API is described as archive so no deletion of information is allowed, account was flaged as deleted and will be perceived as one. If you wish to delete it permanently contact the API administrator."
    )

# Get a user by ID
@users_router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user(user_id: int):
    with Session(engine) as session:
        statement = select(Users).where(Users.id == user_id)
        results = session.exec(statement)
        user = results.first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
                
        return user