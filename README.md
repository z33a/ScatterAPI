# ScatterAPI
## SAVE_DIR Folder Structure
    SAVE_DIR/
    │
    ├── uploads/
    │	└── {upload_id}/
    │		├── thumbnail.jpg
    │		├── metadata.json
    │		└── files/
    │			└── {file_index}.ext
    │
    ├── collections/
    │   └── {collection_id}/
    │	    └── thumbnail.jpg
    │
    └── users/
        └── {user_id}/
            └── profile_picture.jpg

## File Naming Key
- routes.py
    - Contains FastAPI endpoints
- models.py
    - Contains classes for SQLModel and PyDantic
- utils.py
    - Contains misc and helper functions can also be used outside the module
- types.py
    - Contains other classes and enums used in the module