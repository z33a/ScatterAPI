# External imports
from fastapi import UploadFile, HTTPException, status
from moviepy import VideoFileClip
from PIL import Image # PIL = pillow
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

# Internal imports
from config import SAVE_DIR, TEMP_DIR, TARGET_THUMBNAIL_HEIGHT

# Methods directly facing the API (that's why they use UploadFile instead of BytesIO and can raise HTTPException)
def create_upload_thumbnail(file: UploadFile, upload_id: int, is_user_uploaded: bool = False) -> bool:
    thumbnail_location = os.path.join(SAVE_DIR, "uploads", str(upload_id), "thumbnail.jpg")

    file.file.seek(0)

    if is_user_uploaded:
        supported_mimes = ["image/jpeg", "image/png", "image/webp"]

        if file.content_type not in supported_mimes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thumbnail must be only 'image/jpeg', 'image/png' or 'image/webp'!")

    return create_thumbnail(file_mime=file.content_type, file=BytesIO(file.file.read()), thumbnail_location=thumbnail_location)

def create_profile_picture(file: UploadFile, user_id: int):
    supported_mimes = ["image/jpeg", "image/png", "image/webp"]
    profile_picture_location = os.path.join(SAVE_DIR, "users", str(user_id), "profile_picture.jpg")

    if file.content_type in supported_mimes:
        with Image.open(file.file) as img:
            width, height = img.size

            if width != height:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile picture must be 1:1 ratio (for example 512x512 pixel)!")
        
        file.file.seek(0)
        create_thumbnail(file_mime=file.content_type, file=BytesIO(file.file.read()), thumbnail_location=profile_picture_location)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile picture file must be only 'image/jpeg', 'image/png' or 'image/webp'!")

# Generates thumbnail or uses provided one and saves it to disk
def create_thumbnail(file_mime: str, file: BytesIO, thumbnail_location: str, target_height: int = TARGET_THUMBNAIL_HEIGHT) -> bool:
    supported_mimes = ["image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4", "video/webm"]

    thumbnail = None

    if file_mime in supported_mimes:
        # Ensure the save directory exists
        os.makedirs(os.path.dirname(thumbnail_location), exist_ok=True)

        if file_mime == "image/gif":
            # Open the GIF file
            with Image.open(file) as gif:
                # Get the total number of frames in the GIF
                total_frames = gif.n_frames

                # Calculate the 1/10th frame index
                frame_index = int(total_frames / 10)

                # Seek to the frame
                gif.seek(frame_index)

                # Create a thumbnail from the first frame (maybe when implemented downscaling to all types)
                #img.thumbnail(size)

                thumbnail = gif.copy()

                # Save the thumbnail image
                #gif.save(thumbnail_location)
        elif file_mime.split('/')[0] == "video":
            with NamedTemporaryFile(dir=TEMP_DIR) as temp_file:
                # Write the contents of the BytesIO object to the temporary file
                temp_file.write(file.read())

                # Load video from file
                with VideoFileClip(temp_file.name) as video:
                    # Calculate the time for 1/10th of the video duration
                    duration = video.duration
                    time_for_thumbnail = duration / 10
                    
                    # Get the frame at that time
                    frame = video.get_frame(time_for_thumbnail)
                    
                    # Save the frame as an image
                    image = Image.fromarray(frame)

                    thumbnail = image.copy()

                    #image.save(thumbnail_location)
        else:
            # Open the image file
            with Image.open(file) as img:
                thumbnail = img.copy()

        # Get the current size of the image
        width, height = thumbnail.size
        
        # Calculate the new height and width while keeping the aspect ratio
        if height > target_height:
            aspect_ratio = width / height
            target_width = int(target_height * aspect_ratio)
            
            # Resize the image
            thumbnail_resized = thumbnail.resize((target_width, target_height), Image.Resampling.LANCZOS)
        else:
            # If image is smaller than 720p, keep the original
            thumbnail_resized = thumbnail.copy()

        # Convert the image to RGB (if it is not already in RGB mode)
        thumbnail_resized = thumbnail_resized.convert("RGB")

        # Save the image in .jpg format
        thumbnail_resized.save(thumbnail_location, "JPEG")

        return True
    else:
        return False