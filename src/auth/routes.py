# External imports
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

# Internal imports
from users.models import Users
from database import engine
from auth.utils import verify_password, create_token, verify_token
from auth.types import TokenTypes
from auth.models import TokenResponse, RefreshTokenResponse
from users.utils import verify_authenticated_user
from config import ANONYMOUS_USER

auth_router = APIRouter()

# Login and generate token
@auth_router.post("/token", tags=["auth"], response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        statement = select(Users).where(Users.username == form_data.username)
        results = session.exec(statement)
        user = results.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist!")
    else:
        correct_password = verify_password(plain_password=form_data.password, hashed_password=user.password)

        if correct_password:
            access_token = create_token(data={"sub": form_data.username}, token_type=TokenTypes.ACCESS)
            refresh_token = create_token(data={"sub": form_data.username}, token_type=TokenTypes.REFRESH)

            return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password!")

@auth_router.post("/refresh-token", tags=["auth"], response_model=RefreshTokenResponse)
async def refresh_access_token(refresh_token: str = Body(embed=True)):
    token_payload = verify_token(token=refresh_token)
    current_user = verify_authenticated_user(token_payload=token_payload)

    # Maybe not needed - just a fail-safe
    if current_user.username == ANONYMOUS_USER: # Login of anonymous user is not allowed in this endpoint
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided!")

    access_token = create_token(data={"sub": current_user.username}, token_type=TokenTypes.ACCESS)

    return RefreshTokenResponse(access_token=access_token, token_type="bearer")