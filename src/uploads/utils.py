# External imports
import uuid
from datetime import datetime

# Generate a filename for an uploaded file
def generate_filename(extension: str) -> str:
    # Generate a timestamp and UUID
    timestamp = int(datetime.now().timestamp())
    file_uuid = uuid.uuid4()

    # Combine them to form the final filename (e.g., 1731798585_9b1b25cd.jpg)
    filename = f"{timestamp}_{file_uuid}{extension}"
    return filename