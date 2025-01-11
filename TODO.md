# To-do list
This is a todo list of things that should be implemented or changed (it is in no way complete or frequently updated, it mostly serves as notes for developers)

## Global
- [ ] Change all requests from 'example: str = Form(default=None)' to 'example: Annotated[str, Form()] = None' as recommended by FastAPI guide
- [ ] Replace all results.first() with results.one() if only one result should exist and add try-except blocks for error resolution
- [ ] Add metadata/documentation to annotations in methods
- [x] Do not return internal file, thumbnail and profile picture paths to users
- [ ] Make all requests respect 'deleted_at' and not show the item
- [x] Create better way to inject current UNIX time into SQL querries that use PyDantic models
- [ ] Use relationships when returning models like upload (will also include all files) Example: https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships (For now do not do, the API design may not be aligned with it) 
- [x] Remove all unneeded imports
- [x] Change filesystem structure from "/{user_id}/{upload_id}/{files | thumbnail.ext}/image.ext" to "/uploads/{upload_id}/{files | thubmnail.ext | info.json}/image.ext" and "/collections/{collection_id}/thubmnail.ext" and "/users/{user_id}/profile_picture.ext"
- [ ] Add basic 'offset, limit and other filtering' to all 'get all ...' endpoints
- [x] Rewrite all endpoints to use Body (JSON) for requests instead of Form()
- [ ] Simlify endpoints by moving the base path to APIRouter: https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter
- [ ] Implement simple logging of events and errors (like failed file save) using python's built-in logging module
- [ ] Ensure that only files up to specific size (like 20 MiB) can be uploaded by users as thumbnails/profile_pictures
- [x] Better organize classes and enums into correct files

## Database
- [x] Port database logic to SQLModel for simplicity and security
- [x] Implement connection pooling with timeouts and limits (not going to implement - sqlmodel session works similarly)

## Auth
- [ ] Implement refresh token logic

## Uploads
- [ ] Different upload limits based on primary mime type (For example that image can be max 50 MiB but video up to 5 GiB)
- [x] Implement scaling down thumbnail images (either user uploaded or generated)
- [x] Delete a file if the upload was incomplete (for example when the file was too big)
- [x] Cleanup 'new_upload' endpoint
- [x] Allow users to upload json object as a metadata to an archive upload (like scraped from Reddit) and save it in postgres using JSONB (more efficient than JSON)
- [x] Validate json metadata using 'jsonschema'
- [x] Save backup json metadata alongside the files in a upload's directory
- [x] Remove duplicate utils function for generating filename (first check if it is not used, if yes replace with one from files.utils)
- [x] Implement creating thumbnail for gif, video etc.
- [ ] Check all mime types against file extensions before working with them
- [ ] Delete database entry if file upload failed (also applies to users, files etc.)
- [ ] Create background job that would run once a day and downscale all uploaded files and save them alongside original ones (have option in endpoint to choose which version)
- [ ] Rewrite, cleanup and complete order by metadata

## Users
- [ ] Ensure that users can do only what they are authorized to do
- [x] Allow users to upload profile pictures (Just copy thumbnail logic from uploads)
- [x] Figure out how to request form model (pydantic/sqlmodel) and file (UploadFile) while keeping content-type as multipart/form-data in new_user endpoint - Can't be done as said in FastAPI docs: https://fastapi.tiangolo.com/tutorial/request-files/#what-is-form-data
- [x] Cleanup 'new_user' endpoint
- [x] Only allow username without spaces
- [x] Make email optional (because for example bots don't have email)

## Collections
- [ ] Change privacy from [public (everyone) or private (only owner)] to [public (everyone) or private (owner + allowed users)]
- [ ] Allow users to upload thumbnails otherwise generate them from random upload belonging to it (or the latest one, but will need frequent updates)
- [ ] Change internal naming of 'collections' to something different as it interferes with python's own standard library (temporary name 'scatter_collections' applied)
- [ ] Allow users to define order of uploads in a collection using a jsonb column and ids of uploads (if id not specified add to the end of the page), they will also be able to overwrite it by using different order_by on 'get all ...' endpoint

## Tags
- [x] Implement tags for uploads and collections