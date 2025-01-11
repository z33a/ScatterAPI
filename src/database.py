# External imports
from sqlmodel import SQLModel, create_engine, Session, select

# Internal imports
from config import DATABASE_URL, ANONYMOUS_USER
from users.models import Users
from users.types import UserRoles, UserStatuses

engine = create_engine(DATABASE_URL)

def initialize_database():
    SQLModel.metadata.create_all(engine)

def setup_database_defaults():
    anonymous = Users(username=ANONYMOUS_USER, password=None, role=UserRoles.SYSTEM.value, status=UserStatuses.NORMAL.value)

    with Session(engine) as session:
        statement = select(Users).where(Users.username == ANONYMOUS_USER, Users.role == UserRoles.SYSTEM.value)
        results = session.exec(statement)

        if results.first() is None:
            db_user = Users.model_validate(anonymous)
            session.add(db_user)
            session.commit()