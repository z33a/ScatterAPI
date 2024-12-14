# To-do list
This is a todo list of things that should be implemented or changed (it is in no way complete or frequently updated, it mostly serves as notes for developers)

## Global
- [ ] Change all requests from 'example: str = Form(default=None)' to 'example: Annotated[str, Form()] = None' as recommended by FastAPI guide
- [ ] Replace all results.first() with results.one() if only one result should exist and add try-except blocks for error resolution
- [ ] Add metadata/documentation to annotations in methods

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
- [ ] Allow users to upload json object as a metadata to an arcive upload (like scraped from Reddit) and save it in postgres using JSONB (more efficient than JSON)
- [ ] Validate json metadata using 'jsonschema'

## Users
- [ ] Ensure that users can do only what they are authorized to do
- [x] Allow users to upload profile pictures (Just copy thumbnail logic from uploads)
- [ ] Figure out how to request form model (pydantic/sqlmodel) and file (UploadFile) while keeping content-type as multipart/form-data in new_user endpoint (If different content-type, form model is used as object (json) or file as string in Swagger (FastAPI docs))
- [ ] Cleanup 'new_user' endpoint
- [ ] Only allow username without spaces

## Collections
- [ ] Change privacy from public (everyone), private (only owner) to private (owner + allowed users)