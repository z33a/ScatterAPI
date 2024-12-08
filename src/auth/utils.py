# External imports
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Internal imports
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

# OAuth2PasswordBearer provides the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Configure Passlib with Argon2
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=12288,  # Memory usage in KB
    argon2__time_cost=3,        # Number of iterations
    argon2__parallelism=1       # Number of threads
)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Enum for token types
class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

# Function to create tokens
def create_token(data: dict, token_type: TokenType) -> str:
    if token_type == TokenType.ACCESS:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == token_type.REFRESH:
        expires_delta = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": token_type.value})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    if token:
        # Decode/extract info from refresh token
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired!")
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")
    else:
        return None