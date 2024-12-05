# External imports
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, or_

# Internal imports
from users.models import User, UserCreate, UserResponse
from database import engine
from auth.utils import hash_password
from users.utils import check_password_structure, verify_authenticated_user
from config import ANONYMOUS_USER

users_router = APIRouter()

# Sign up and create a new user
@users_router.post("/users", tags=["users"], response_model=UserResponse)
async def new_user(new_user: UserCreate):
    with Session(engine) as session:
        statement = select(User).where(or_(User.username == new_user.username, User.email == new_user.email))
        results = session.exec(statement)

        if results.first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this username or email already exists!")

    if check_password_structure(new_user.password):
        hashed_password = hash_password(new_user.password)
        new_user.password = hashed_password

        with Session(engine) as session:
            db_user = User.model_validate(new_user)
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
        statement = select(User)
        results = session.exec(statement)

        return results.all()

# Get a user logged in by the token !!! Must be before '/users/{user_id}' endpoint !!!
@users_router.get("/users/me", tags=["users"], response_model=UserResponse)
async def get_authenticated_user(current_user: UserResponse = Depends(verify_authenticated_user)):
    if current_user.username == ANONYMOUS_USER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or no token provided!")

    return current_user

# Update a user logged in by the token
@users_router.put("/users/me", tags=["users"], response_model=UserResponse)
async def update_authenticated_user(current_user: UserResponse = Depends(verify_authenticated_user)):
    pass

# Delete a user logged in by the token
@users_router.delete("/users/me", tags=["users"], response_model=str)
async def delete_authenticated_user(current_user: UserResponse = Depends(verify_authenticated_user)):
    return "User 'user' deleted successfully."

# Get a user by ID
@users_router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        results = session.exec(statement)
        user = results.first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
                
        return user