# External imports
from sqlmodel import SQLModel, create_engine

# Internal imports
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)

def initialize_database():
    SQLModel.metadata.create_all(engine)