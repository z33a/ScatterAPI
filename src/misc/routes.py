# External imports
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
import os
from typing import List, Tuple

# Internal imports
from misc.models import Health

misc_router = APIRouter()

@misc_router.get("/health", tags=["miscc"], response_model=Health)
async def health_check():
    return {"status": "healthy"}