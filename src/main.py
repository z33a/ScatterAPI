# External imports
from fastapi import FastAPI
import uvicorn

# Internal imports
from auth.routes import auth_router
from users.routes import users_router
from uploads.routes import uploads_router
from files.routes import files_router
from misc.routes import misc_router
from database import initialize_database, setup_database_defaults
from config import PORT

app = FastAPI(
    title="FastAPI",
    description="This is a main API for the Eclipse Archive",
    version="0.0.6"
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(uploads_router)
app.include_router(files_router)
app.include_router(misc_router)

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the API, for documentation open '/docs' or '/redoc'"}

@app.on_event("startup")
def on_startup():
    initialize_database()
    setup_database_defaults()

# Entry point for running with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)