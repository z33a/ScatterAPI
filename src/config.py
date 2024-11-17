# External imports
from dotenv import load_dotenv
import os

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

FORBIDDEN_ACCOUNTS_LOGIN = ["Anonymous"]

# Uploads
UPLOAD_TYPE_FILE_SIZE_TRESHOLD = os.getenv("UPLOAD_TYPE_FILE_SIZE_TRESHOLD", 10 * 1024 * 1024) # Default is 10MB
MAX_UPLOAD_SIZE = os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024) # Default is 50MB
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/mnt/storage/Code/Projects/Scatter/ScatterTest/01-python/filesystem")