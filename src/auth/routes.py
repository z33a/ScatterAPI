# External imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Internal imports
from auth.utils import create_access_token, verify_password
from database import fetch_query
from auth.models import Token
from config import FORBIDDEN_ACCOUNTS_LOGIN

auth_router = APIRouter()

# Login and generate token
@auth_router.post("/token", tags=["auth"], response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username in FORBIDDEN_ACCOUNTS_LOGIN:
        raise HTTPException(status.HTTP_423_LOCKED, detail="Login to this account is disabled!")

    # Fetch the user from the database
    user = fetch_query("SELECT * FROM users WHERE username = %s", (form_data.username,))
    
    if not user or not verify_password(form_data.password, user[0]["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

