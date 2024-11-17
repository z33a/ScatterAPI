# External imports
from pydantic import BaseModel
from typing import List
from datetime import datetime

class UploadNew(BaseModel):
    message: str
    name: str
    upload_type: str
    file_paths: List[str]

class UploadNewInfo(BaseModel):
    name: str
    description: str

class Upload(BaseModel):
    title: str
    description: str
    upload_type: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    file_links: List[str]