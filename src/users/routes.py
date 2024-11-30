# External imports
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer

# Internal imports
from users.models import User, UserCreate, UserResponse
from database import engine
from auth.utils import hash_password, verify_token
from users.utils import check_password

users_router = APIRouter()

# OAuth2PasswordBearer provides the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Sign up and create a new account
@users_router.post("/users", tags=["users"], response_model=UserResponse)
async def new_user(new_user: UserCreate):
    with Session(engine) as session:
        statement = select(User).where(User.username == new_user.username)
        results = session.exec(statement)

        if results.first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this username already exists!")

    with Session(engine) as session:
        statement = select(User).where(User.email == new_user.email)
        results = session.exec(statement)

        if results.first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists!")

    if check_password(new_user.password):
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

# Protected route (requires authentication) !!! Must be before '/users/{user_id}' endpoint !!!
@users_router.get("/users/me", tags=["users"], response_model=UserResponse)
async def get_authorized_user(token: str):
    print(1)
    token_payload = verify_token(token)
    print(token_payload)
    
    with Session(engine) as session:
        statement = select(User).where(User.username == token_payload["sub"])
        results = session.exec(statement)
        user = results.first()

        return user

# Get a user by ID
@users_router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user(user_id: int):
    pass