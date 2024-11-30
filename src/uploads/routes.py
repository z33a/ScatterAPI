# External imports
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status

# Internal imports
#from uploads.models import UploadNew, UploadNewInfo, Upload
#from uploads.utils import generate_filename
#from users.dependencies import check_token
#from database import fetch_query, execute_query
#from config import UPLOAD_DIR, UPLOAD_TYPE_FILE_SIZE_TRESHOLD

# Main code
uploads_router = APIRouter()

@uploads_router.post("/uploads", tags=["uploads"])
async def new_upload(files: list[UploadFile] = File(...)):
    pass

@uploads_router.get("/uploads", tags=["uploads"])
async def get_all_uploads():
    pass

@uploads_router.get("/uploads/{upload_id}", tags=["uploads"])
async def get_upload(upload_id: int):
    pass