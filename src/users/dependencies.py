# External imports
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Optional

# Internal imports
from config import SECRET_KEY, ALGORITHM
from database import fetch_query

# OAuth2PasswordBearer dependency for extracting tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Dependency to get the current user from the token
def check_token(token: str = Depends(oauth2_scheme)):
    if token is None:
        return None  # No token provided, the user is anonymous.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        else:
            user = fetch_query("SELECT id, status FROM users WHERE username = %s", (username,))
            if user is None:
                raise credentials_exception
            elif user[0]['status'] == "banned":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is banned and cannot log in. Contact api administrator for potential solution.")
            elif user[0]['status'] == "normal":
                return user[0]['id'], username
            else:
                raise credentials_exception
    except JWTError:
        raise credentials_exception
