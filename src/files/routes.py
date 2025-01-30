# External imports
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse as FileResponseFastAPI
from sqlmodel import Session, select
import os

# Internal imports
from files.models import Files, FileResponse
from database import engine
from config import SAVE_DIR
from utils import build_sqlmodel_get_all_query

files_router = APIRouter()

@files_router.get("/files", tags=["files"], response_model=list[FileResponse])
async def get_all_files(offset: int = 0, limit: int | None = 100, upload_id: int | None = None, created_before: int | None = None, created_after: int | None = None, created_by: int | None = None, order_by: str | None = None, order_by_direction: str | None =  None):
    with Session(engine) as session:
        additional_filters = []
        if upload_id is not None:
            additional_filters.append(Files.upload_id == upload_id)

        statement = build_sqlmodel_get_all_query(model=Files, offset=offset, limit=limit, created_before=created_before, created_after=created_after, created_by=created_by, additional_filters=additional_filters)
        
        results = session.exec(statement)

        return results.all()

@files_router.get("/files/{file_id}", tags=["files"], response_model=FileResponse)
async def get_file(file_id: int):
    with Session(engine) as session:
        statement = select(Files).where(Files.id == file_id)
        results = session.exec(statement)
        file = results.one()

        if file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found!")
                
        return file

@files_router.get("/files/{file_id}/download", tags=["files"], response_class=FileResponseFastAPI)
async def download_file(file_id: int):
    with Session(engine) as session:
        statement = select(Files).where(Files.id == file_id)
        results = session.exec(statement)
        file = results.one()

        if file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found!")
        
        file_path = os.path.join(SAVE_DIR, "uploads", str(file.upload_id), "files", f"{file.generated_filename}.{file.file_ext}")

        if os.path.exists(file_path):
            return file_path
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found!")