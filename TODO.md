# To-do list
This is a todo list of things that should be implemented or changed (it is in no way complete or frequently updated, it mostly serves as notes for developers)
## Database
- [x] Port database logic to SQLModel for simplicity and security
- [x] Implement connection pooling with timeouts and limits (not going to implement - sqlmodel session works similarly)

## Auth
- [ ] Implement unsave and save refresh token receiving in auth.py

## Uploads
- [ ] Different upload limits based on primary mime type
- [ ] Implement scaling down thumbnail images (either user uploaded or generated)
- [ ] Delete a file if the upload was incomplete (for example when the file was too big)

## Users
- [ ] Ensure that users can do only what they are authorized to do