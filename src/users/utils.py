# External imports
import re
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

# Internal imports
from auth.utils import verify_token
from users.models import User, UserResponse
from database import engine
from users.types import UserRoles, UserStatuses
from config import ANONYMOUS_USER

def check_password_structure(password) -> bool:
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if password contains at least one uppercase letter, one lowercase letter, one digit, and one special symbol
    if not re.search(r'[A-Z]', password):  # At least one uppercase letter
        return False

    if not re.search(r'[a-z]', password):  # At least one lowercase letter
        return False

    if not re.search(r'[0-9]', password):  # At least one number
        return False

    if not re.search(r'[\W_]', password):  # At least one special symbol
        return False

    # If all conditions are met
    return True

def verify_authenticated_user(token_payload: dict | None = Depends(verify_token)) -> UserResponse:
    with Session(engine) as session:
        if token_payload:
            statement = select(User).where(User.username == token_payload.get("sub"))
        else:
            statement = select(User).where(User.username == ANONYMOUS_USER, User.role == UserRoles.SYSTEM.value)
            
        results = session.exec(statement)
        user = results.first()

        if user is None:
            if token_payload:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured on the side of the server! Please contact the API administrator about this issue. Error-reason: user object returned None")
        
        if user.status is UserStatuses.BANNED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User is banned and cannot login! Status detail: {user.status_detail}")
        elif user.status is UserStatuses.DELETED:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        elif user.role is UserRoles.SYSTEM:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="System/Internal users cannot login!")

        return user