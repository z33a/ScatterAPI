# External imports
from pydantic import BaseModel
from datetime import datetime

class File(BaseModel):
    file_id: int
    upload_id: int