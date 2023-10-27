from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class Genre(str, Enum):
    action = 'action'
    adventure = 'adventure'
    romance = 'romance'
    fantasy = 'fantasy'
    science_fiction = 'science fiction'
    dystopian = 'dystopian'
    horror = 'horror'


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None


class UserList(BaseModel):
    users: list[UserPublic]


class Message(BaseModel):
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class BookSchema(BaseModel):
    name: str
    author: str
    description: str
    genre: list[Genre]
    number_pages: int


class BookPublic(BookSchema):
    user_id: int
    id: str


class BookList(BaseModel):
    books: list[BookPublic]
