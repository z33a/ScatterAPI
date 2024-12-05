# External imports
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status

# Internal imports
from uploads.models import Upload, UploadResponse
from users.models import UserResponse
from users.utils import verify_authenticated_user
#from users.dependencies import check_token
#from database import fetch_query, execute_query
#from config import UPLOAD_DIR, UPLOAD_TYPE_FILE_SIZE_TRESHOLD

# Main code
uploads_router = APIRouter()

@uploads_router.post("/uploads", tags=["uploads"], response_model=UploadResponse)
async def new_upload(files: list[UploadFile] = File(...), title: str = Form(...), description: str = Form(...)):
    pass

@uploads_router.get("/uploads", tags=["uploads"])
async def get_all_uploads():
    pass

@uploads_router.get("/uploads/{upload_id}", tags=["uploads"])
async def get_upload(upload_id: int):
    pass