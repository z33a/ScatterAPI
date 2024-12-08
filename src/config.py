# External imports
from dotenv import load_dotenv
import os

load_dotenv()

# FastAPI
PORT = int(os.getenv("PORT", 8000))

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
ANONYMOUS_USER = os.getenv("ANONYMOUS_USER", "Anonymous")

# Tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)) # Access token default is 60 minutes (1 hour)
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 10080)) # Refresh token default is 10080 minutes (7 days)

# Uploads
MAX_FILE_SIZE = os.getenv("MAX_UPLOAD_SIZE", 2000 * 1024 * 1024) # Default is 50MB
FILE_READ_CHUNK = os.getenv("FILE_READ_CHUNK", 1024) # Size of a chunk to be read from an uploaded file at time. Default is 1MB
UPLOAD_DIR = os.getenv("UPLOAD_DIR")