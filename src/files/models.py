# External imports
from sqlmodel import Field, Session, SQLModel, create_engine, select
import datetime
from decimal import Decimal

# Internal imports

class FileBase(SQLModel):
    upload_id: int = Field(foreign_key="uploads.id")
    original_filename: str
    generated_filename: str # Example: '1733620946_c1da59f9-8465-4e8d-9b93-06dee6b0ee04'
    file_location: str # Example: '/{user_id}/{post_id}/files'
    file_size: int
    file_mime: str
    file_ext: str # Example: '.png'
    created_by: int = Field(foreign_key="users.id")
    
class Files(FileBase, table=True): # Id is optional because it is generated by the databse (just leave it like that and don't think about it too much)
    id: int | None = Field(default=None, primary_key=True)
    created_at: Decimal
    deleted_at: Decimal | None = Field(default=None)

class FileCreate(FileBase):
    pass

class FileResponseSQL(FileBase):
    id: int
    created_at: Decimal