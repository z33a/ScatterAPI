# External imports
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
import os
from typing import List, Tuple

# Internal imports
from uploads.models import UploadNew, UploadNewInfo, Upload
from uploads.utils import generate_filename
from users.dependencies import check_token
from database import fetch_query, execute_query
from config import UPLOAD_DIR, UPLOAD_TYPE_FILE_SIZE_TRESHOLD

uploads_router = APIRouter()

@uploads_router.post("/uploads", tags=["uploads"], response_model=UploadNew)
async def new_upload(files: List[UploadFile] = File(...), upload_info_title: str = Form(...), upload_info_description: str = Form(...), current_user: Tuple[int, str] = Depends(check_token)):
    # Check if title already exists
    upload = fetch_query("SELECT * FROM uploads WHERE title = %s", (upload_info_title,))
    if upload is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Upload with the same title already exists!")
    
    if current_user is None:
        created_by = fetch_query("SELECT id FROM users WHERE username = 'Anonymous'")[0]['id']
    else:
        created_by = current_user[0]

    file_count = 0
    image_count = 0

    for file in files:
        mime_type = file.content_type
        mime_file_type = mime_type.split("/")[0]

        if mime_file_type == "image":
            image_count += 1
        
        file_count += 1

    if file_count == 1 and image_count == 1:
        upload_type = "single-image"
    elif file_count == 1 and image_count == 0:
        upload_type = "single-file"
    elif file_count > 1 and image_count == file_count:
        upload_type = "multiple-image"
    elif file_count > 1 and image_count == 0:
        upload_type = "multiple-file"
    elif file_count > 1 and image_count != file_count and image_count > 0:
        upload_type = "multiple-mixed"
    else:
        upload_type = "unknown"

    execute_query("INSERT INTO uploads (title, description, type, created_by) VALUES (%s, %s, %s, %s)", (upload_info_title, upload_info_description, upload_type, created_by))
    upload_id = fetch_query("SELECT id FROM uploads WHERE title = %s", (upload_info_title,))[0]['id']

    file_paths = []

    for file in files:
        # Extract the file extension
        _, file_extension = os.path.splitext(file.filename)

        generated_file_name = generate_filename(file_extension)
        file_path = os.path.join("https://scatter.z33a.site/", str(created_by), str(upload_id), generated_file_name)

        file_paths.append(file_path)

        file_mime = file.content_type

        # Check the file size before deciding how to process it
        if file.size <= UPLOAD_TYPE_FILE_SIZE_TRESHOLD:
            # For smaller files, read the entire file into memory
            contents = await file.read()
            save_target = os.path.join(UPLOAD_DIR, str(created_by), str(upload_id), generated_file_name)
            os.makedirs(os.path.dirname(save_target), exist_ok=True)
            
            # Save the file entirely in memory
            with open(save_target, "wb") as f:
                f.write(contents)
        else:
            # For larger files, stream the file in chunks
            save_path = os.path.join("uploads", file.filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Open the file for writing asynchronously
            async with aiofiles.open(save_path, 'wb') as out_file:
                while chunk := await file.read(1024 * 1024):  # Read in 1 MB chunks
                    await out_file.write(chunk)

        execute_query("INSERT INTO files (upload_id, original_file_name, generated_file_name, file_link, file_size, file_mime, file_ext, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (upload_id, file.filename, generated_file_name, file_path, 1000, file_mime, file_extension, created_by))
    
    return {"message": "New upload created successfully", "name": upload_info_title, "upload_type": upload_type, "file_paths": file_paths}

@uploads_router.get("/uploads", tags=["uploads"], response_model=List[Upload])
async def get_all_uploads():
    all_uploads = fetch_query("SELECT title, description, type, created_by, created_at, updated_at FROM uploads")

@uploads_router.get("/uploads/{upload_id}", tags=["uploads"], response_model=Upload)
async def get_upload(upload_id: int):
    upload = fetch_query("SELECT * FROM uploads WHERE id = %s", (upload_id,))
    print(upload)
    if upload == []:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This upload does not exist!")

    upload = upload[0]

    upload_file_links = fetch_query("SELECT file_link FROM files WHERE upload_id = %s", (upload_id,))

    file_links = []

    for link in upload_file_links:
        file_links.append(link["file_link"])

    return {
        "title": upload["title"],
        "description": upload["description"],
        "upload_type": upload["type"],
        "created_by": upload["created_by"],
        "created_at": upload["created_at"],
        "updated_at": upload["updated_at"],
        "file_links": file_links
    }

