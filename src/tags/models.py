# External imports
from sqlmodel import Field, SQLModel
from decimal import Decimal

# Internal imports
from utils import current_timestamp

class TagBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)

class Tags(TagBase, table=True):
    id: int | None = Field(default=None, primary_key=True) # Id is optional because it is generated by the database (just leave it like that)
    created_by: int = Field(foreign_key="users.id")
    created_at: Decimal = Field(default_factory=current_timestamp)
    updated_at: Decimal = Field(default_factory=current_timestamp)
    deleted_at: Decimal | None = Field(default=None)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_by: int
    created_at: Decimal
    updated_at: Decimal

class TagCollectionLinks(SQLModel, table=True):
    tag_id: int | None = Field(default=None, foreign_key="tags.id", primary_key=True)
    collection_id: int | None = Field(default=None, foreign_key="collections.id", primary_key=True)
    created_at: Decimal = Field(default_factory=current_timestamp)
    created_by: int = Field(foreign_key="users.id")

class TagUploadLinks(SQLModel, table=True):
    tag_id: int | None = Field(default=None, foreign_key="tags.id", primary_key=True)
    upload_id: int | None = Field(default=None, foreign_key="uploads.id", primary_key=True)
    created_at: Decimal = Field(default_factory=current_timestamp)
    created_by: int = Field(foreign_key="users.id")