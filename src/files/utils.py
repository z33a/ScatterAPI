# External import
from fastapi import HTTPException, status, UploadFile
import aiofiles
from sqlmodel import Session
import os
import uuid
import datetime

# Internal imports
from config import FILE_READ_CHUNK
from database import engine
from files.models import FileCreate, Files, FileResponseSQL

def generate_filename() -> str:
    # Generate a timestamp and UUID
    timestamp = int(datetime.datetime.now(datetime.UTC).timestamp())
    file_uuid = uuid.uuid4()
    return f"{timestamp}_{file_uuid}"

def create_file(file: UploadFile, upload_id: int, file_location: str, file_size: int, created_by: int, generated_filename: str) -> FileResponseSQL:
    file_mime = file.content_type

    # Extract the file extension
    original_filename, file_ext = os.path.splitext(file.filename)

    new_file = FileCreate(upload_id=upload_id, original_filename=original_filename, generated_filename=generated_filename, file_location=file_location, file_size=file_size, file_mime=file_mime, file_ext=file_ext, created_by=created_by)

    with Session(engine) as session:
        db_file = Files.model_validate(new_file)
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
        return db_file

async def stream_save_file(file: UploadFile, target: str, max_size: int | None) -> int:
    total_size = 0  # Initialize size tracker

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)

        file.file.seek(0)  # Rewind to the beginning of the file

        async with aiofiles.open(target, "wb") as out_file:
            while content := await file.read(FILE_READ_CHUNK):
                total_size += len(content)  # Increment total size

                if max_size is not None and total_size > max_size:  # Check if size exceeds limit
                    os.remove(target)
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File exceeds maximum allowed size of {max_size} bytes!")

                await out_file.write(content)

        return total_size
    except HTTPException as e:
        raise e  # Propagate custom exceptions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading file: {str(e)}")