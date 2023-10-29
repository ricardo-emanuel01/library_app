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


class StatusTrade(str, Enum):
    awaiting_approval = 'awaiting approval'
    declined = 'declined'
    approved = 'approved'


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    genre1: Genre
    genre2: Genre
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    genre1: Genre
    genre2: Genre

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    genre1: Genre | None = None
    genre2: Genre | None = None


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


class BookPublicUnauthenticated(BookSchema):
    id: str


class BookPublic(BookPublicUnauthenticated):
    user_id: int


class BookList(BaseModel):
    books: list[BookPublic]


class Trade(BaseModel):
    receiver_id: int
    book_requested: str
    book_offered: str


class TradeViwer(Trade):
    status: StatusTrade
    id: str
    sender_id: int
    year: int
    month: int
    day: int
    hour: int
