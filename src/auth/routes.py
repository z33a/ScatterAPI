# External imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

# Internal imports
from users.models import Users
from database import engine
from auth.utils import verify_password, create_token, TokenType
from auth.models import Token

auth_router = APIRouter()

# Login and generate token
@auth_router.post("/token", tags=["auth"], response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        statement = select(Users).where(Users.username == form_data.username)
        results = session.exec(statement)
        user = results.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist!")
    else:
        correct_password = verify_password(form_data.password, user.password)

        if correct_password:
            access_token = create_token({"sub": form_data.username}, TokenType.ACCESS)
            refresh_token = create_token({"sub": form_data.username}, TokenType.REFRESH)

            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password!")

@auth_router.post("/refresh-token", tags=["auth"])
async def refresh_access_token(refresh_token: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This endpoint is still under development!")