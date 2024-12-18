# External imports
from sqlmodel import Field, SQLModel
import datetime
from decimal import Decimal

# Internal imports
from users.types import UserRoles, UserStatuses

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    description: str | None = Field(default=None)

class Users(UserBase, table=True): # Id is optional because it is generated by the databse (just leave it like that and don't think about it too much)
    id: int | None = Field(default=None, primary_key=True)
    password: str | None # Does not have default=None because it is indented that user must explicitly say no password is provided (so it is not a mistake)
    role: str = Field(default=UserRoles.USER.value)
    status: str = Field(default=UserStatuses.NORMAL.value)
    status_detail: str | None = Field(default=None) # For example for setting unban date
    profile_picture_location: str | None = None
    created_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    updated_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    deleted_at: Decimal | None = Field(default=None)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    status: str
    status_detail: str | None
    profile_picture_location: str | None
    created_at: Decimal
    updated_at: Decimal

class UserDeletionResponse(SQLModel):
    message: str
    disclaimer: str