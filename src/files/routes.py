# External imports
from fastapi import APIRouter, HTTPException, Depends
from typing import List

# Internal imports
from files.models import File

files_router = APIRouter()

# Get all files
@files_router.get("/files", tags=["files"], response_model=List[File])
async def get_all_files():
    pass

@files_router.get("/files/{file_id}", tags=["files"], response_model=File)
async def get_file():
    pass