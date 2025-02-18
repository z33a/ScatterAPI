# External imports
from sqlmodel import Field, SQLModel, Column
from decimal import Decimal
from sqlalchemy.dialects.postgresql import JSONB

# Internal imports
from utils import current_timestamp

class UploadBase(SQLModel):
    title: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)

class Uploads(UploadBase, table=True):
    id: int | None = Field(default=None, primary_key=True) # Id is optional because it is generated by the databse (just leave it like that)
    type: str
    metadata_type: str | None = Field(default=None)
    metadata_json: dict | None = Field(sa_column=Column(JSONB))
    created_by: int = Field(foreign_key="users.id")
    created_at: Decimal = Field(default_factory=current_timestamp)
    updated_at: Decimal = Field(default_factory=current_timestamp)
    deleted_at: Decimal | None = Field(default=None)

class UploadCreate(UploadBase):
    pass

class UploadResponse(UploadBase):
    id: int
    type: str
    metadata_type: str | None
    metadata_json: dict | None
    created_by: int
    created_at: Decimal
    updated_at: Decimal