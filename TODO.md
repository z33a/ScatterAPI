# To-do list
This is a todo list of things that should be implemented or changed (it is in no way complete or frequently updated, it mostly serves as notes for developers)

## Global
- [ ] Change all requests from 'example: str = Form(default=None)' to 'example: Annotated[str, Form()] = None' as recommended by FastAPI guide
- [ ] Replace all results.first() with results.one() if only one result should exist and add try-except blocks for error resolution
- [ ] Add metadata/documentation to annotations in methods
- [ ] Do not return internal file, thumbnail and profile picture paths to users
- [ ] Make all requests respect 'deleted_at' and not show the item
- [ ] Create better way to inject current UNIX time into SQL querries that use PyDantic models

## Database
- [x] Port database logic to SQLModel for simplicity and security
- [x] Implement connection pooling with timeouts and limits (not going to implement - sqlmodel session works similarly)

## Auth
- [ ] Implement unsave and save refresh token receiving
- [ ] Implement refresh token logic

## Uploads
- [ ] Different upload limits based on primary mime type
- [ ] Implement scaling down thumbnail images (either user uploaded or generated)
- [ ] Delete a file if the upload was incomplete (for example when the file was too big)
- [ ] Cleanup 'new_upload' endpoint
- [ ] Add check if collection exists before creating upload
- [x] Allow users to upload json object as a metadata to an archive upload (like scraped from Reddit) and save it in postgres using JSONB (more efficient than JSON)
- [ ] Validate json metadata using 'jsonschema'

## Users
- [ ] Ensure that users can do only what they are authorized to do
- [x] Allow users to upload profile pictures (Just copy thumbnail logic from uploads)
- [ ] Figure out how to request form model (pydantic/sqlmodel) and file (UploadFile) while keeping content-type as multipart/form-data in new_user endpoint (If different content-type, form model is used as object (json) or file as string in Swagger (FastAPI docs))
- [ ] Cleanup 'new_user' endpoint
- [ ] Only allow username without spaces
- [ ] Make email optional and do not use it as unique indetificator (because for example bots don't have email)

## Collections
- [ ] Change privacy from [public (everyone) or private (only owner)] to [public (everyone) or private (owner + allowed users)]
- [ ] Allow users to upload thumbnails otherwise generate them from random upload belonging to it (or the latest one, but will need frequent updates and writing to disk)
- [ ] Change internal naming of 'collections' to something different as it interferes with python's own standard library (temporary name 'scatter_collections' applied)

## Tags
- [ ] Implement tags for uploads and collections