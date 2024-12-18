# External imports
from sqlmodel import Field, Session, SQLModel, create_engine, select
import datetime
from decimal import Decimal

class UploadBase(SQLModel):
    title: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)

class Uploads(UploadBase, table=True): # Id is optional because it is generated by the databse (just leave it like that and don't think about it too much)
    id: int | None = Field(default=None, primary_key=True)
    type: str
    thumbnail_location: str | None = Field(default=None)
    created_by: int = Field(foreign_key="users.id")
    created_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    updated_at: Decimal = Field(default=datetime.datetime.now(datetime.UTC).timestamp())
    deleted_at: Decimal | None = Field(default=None)

class UploadCreate(UploadBase):
    pass

class UploadResponse(UploadBase):
    id: int
    type: str
    thumbnail_location: str | None
    created_by: int
    created_at: Decimal
    updated_at: Decimal