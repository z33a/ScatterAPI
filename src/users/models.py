# External imports
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    user_id: int
    username: str
    email: str
    joined_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserCreateResponse(BaseModel):
    message: str
    username: str