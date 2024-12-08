# External imports
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from fastapi.responses import FileResponse
from sqlmodel import Session, select
import os

# Internal imports
from files.models import Files, FileResponseSQL
from database import engine
from config import UPLOAD_DIR

# Main code
files_router = APIRouter()

@files_router.get("/files", tags=["files"], response_model=list[FileResponseSQL])
async def get_all_files():
    with Session(engine) as session:
        statement = select(Files).where(Files.deleted_at == None)
        results = session.exec(statement)

        return results.all()

@files_router.get("/files/{file_id}", tags=["files"], response_model=FileResponseSQL)
async def get_file(file_id: int):
    with Session(engine) as session:
        statement = select(Files).where(Files.id == file_id)
        results = session.exec(statement)
        file = results.first()

        if file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
                
        return file

@files_router.get("/files/{file_id}/download", tags=["files"], response_class=FileResponse)
async def download_file(file_id: int):
    with Session(engine) as session:
        statement = select(Files).where(Files.id == file_id)
        results = session.exec(statement)
        file = results.first()

        if file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found!")
        
        file_path = os.path.join(UPLOAD_DIR, file.file_location, f"{file.generated_filename}{file.file_ext}")

        if os.path.exists(file_path):
            return file_path
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found!")