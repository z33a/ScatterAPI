# External import
from fastapi import HTTPException, status, UploadFile
import aiofiles
from sqlmodel import Session
import os
import mimetypes

# Internal imports
from config import FILE_READ_CHUNK, SAVE_DIR, MAX_FILE_SIZE
from database import engine
from files.models import Files, FileResponse

# Creates db entry of the file and saves the file to disk (Probably just for POST /uploads endpoint)
async def create_file(file: UploadFile, upload_id: int, filename: str, created_by: int) -> FileResponse:
    file_mime = file.content_type

    original_filename, file_ext = os.path.splitext(file.filename)
    file_ext = file_ext[1:] # Remove the dot

    if file_mime != mimetypes.guess_type(file.filename)[0]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File mime '{file_mime}' is not affiliated with file extension '{file_ext}'!")

    generated_filename = filename

    file_location = os.path.join("uploads", str(upload_id), "files")

    file_size = await stream_save_file(file=file, target=os.path.join(SAVE_DIR, file_location, f"{generated_filename}.{file_ext}"))

    new_file = Files(upload_id=upload_id, original_filename=original_filename, generated_filename=generated_filename, file_location=file_location, file_size=file_size, file_mime=file_mime, file_ext=file_ext, created_by=created_by)

    with Session(engine) as session:
        db_file = Files.model_validate(new_file)
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
        return db_file

async def stream_save_file(file: UploadFile, target: str, max_file_size: int | None = MAX_FILE_SIZE) -> int:
    file_size = 0  # Initialize size tracker

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)

        await file.seek(0) # Rewind to the beginning of the file (must be await as it is async method: https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)

        async with aiofiles.open(target, "wb") as out_file:
            while content := await file.read(FILE_READ_CHUNK):
                file_size += len(content)  # Increment total size

                if max_file_size is not None and file_size > max_file_size: # Check if size exceeds limit
                    os.remove(target)
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File exceeds maximum allowed size of {max_size} bytes!")

                await out_file.write(content)

        return file_size
    except HTTPException as e:
        raise e  # Propagate custom exceptions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading file: {str(e)}")

def save_file(file_path: str, data: bytes):
    try:
        with open(file_path, "wb") as file:
            file.write(data)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")