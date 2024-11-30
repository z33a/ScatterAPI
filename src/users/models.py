# External imports
from sqlmodel import Field, Session, SQLModel, create_engine, select
import datetime
from decimal import Decimal

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)

class User(UserBase, table=True): # Id is optional because it is generated by the databse (just leave it like that and don't think about it too much)
    id: int | None = Field(default=None, primary_key=True)
    password: str
    role: str = Field(default="user")
    status: str = Field(default="normal")
    created_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    updated_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    deleted_at: Decimal | None = Field(default=None)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    status: str
    created_at: Decimal
    updated_at: Decimal