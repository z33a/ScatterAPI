# External imports
from fastapi import APIRouter, HTTPException, Depends
from typing import List

# Internal imports
#from files.models import File

# Main code
files_router = APIRouter()

@files_router.get("/files", tags=["files"])
async def get_all_files():
    pass

@files_router.get("/files/{file_id}", tags=["files"])
async def get_file():
    pass