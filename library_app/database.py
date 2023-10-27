from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from library_app.models import User
from library_app.schemas import UserUpdate
from library_app.settings import Settings

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
username = settings.DATABASE_MONGO_USERNAME
password = settings.DATABASE_MONGO_PASSWORD


uri = f'mongodb+srv://{username}:{password}@cluster0.7rnden3.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(uri, server_api=ServerApi('1'))


mongodb = client['library_app']
booksdb = mongodb['books']


def get_session():
    with Session(engine) as session:
        yield session


def patch_user(user: User, new_user: UserUpdate, session: Session):
    for key, value in new_user.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
