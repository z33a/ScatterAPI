# External imports
from fastapi import FastAPI
import uvicorn

# Internal imports
from auth.routes import auth_router
from users.routes import users_router
from uploads.routes import uploads_router
from files.routes import files_router
from misc.routes import misc_router
from database import initalize_database

app = FastAPI(
    title="FastAPI",
    description="This is a custom API documentation with various features.",
    version="0.0.4"
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(uploads_router)
app.include_router(files_router)
app.include_router(misc_router)

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the API, for documentation open '/docs'"}

@app.get("/initialize", tags=["root"])
async def initialize():
    initalize_database()

# Add an entry point for running with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)