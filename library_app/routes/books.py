from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from library_app.database import booksdb
from library_app.models import User
from library_app.query_builder import query_builder
from library_app.schemas import (
    BookPublic,
    BookPublicUnauthenticated,
    BookSchema,
    Message,
)
from library_app.security import get_current_user

router = APIRouter(prefix='/book', tags=['book'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Type = Annotated[str, Query(max_length=3, alias='type of filter')]
UserId = Annotated[int | None, Query(ge=1, alias='user id')]
Genre1 = Annotated[str | None, Query(max_length=15, alias='genre')]
Genre2 = Annotated[str | None, Query(max_length=15, alias='second genre')]
BookName = Annotated[str | None, Query(max_length=50, alias='title')]
Author = Annotated[str | None, Query(max_length=30, alias='author name')]
Skip = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1)]


@router.get('/', response_model=list[BookPublic])
def get_books(
    user: CurrentUser,
    type: Type = 'or',
    user_id: UserId = None,
    genre1: Genre1 = None,
    genre2: Genre2 = None,
    book_name: BookName = None,
    author: Author = None,
    skip: Skip = 0,
    limit: Limit = 10,
):
    query = query_builder(
        type, genre1, genre2, book_name, author, user_id=user_id
    )

    books = list(booksdb.find(query, skip=skip, limit=limit))

    if not books:
        raise HTTPException(
            detail='not found', status_code=status.HTTP_404_NOT_FOUND
        )

    for book in books:
        str_id = str(book['_id'])
        book.pop('_id')
        book['id'] = str_id

    return books


@router.get('/books', response_model=list[BookPublicUnauthenticated])
def get_books_unauthenticated(
    type: Type = 'or',
    genre1: Genre1 = None,
    genre2: Genre2 = None,
    book_name: BookName = None,
    author: Author = None,
    skip: Skip = 0,
    limit: Limit = 10,
):
    """
    Endpoint to show the books on the platform without expose user
    """
    query = query_builder(
        type, genre1, genre2, book_name, author, user_id=None
    )

    books = list(booksdb.find(query, skip=skip, limit=limit))

    if not books:
        raise HTTPException(
            detail='not found', status_code=status.HTTP_404_NOT_FOUND
        )

    for book in books:
        book.pop('user_id')
        str_id = str(book['_id'])
        book.pop('_id')
        book['id'] = str_id

    return books


@router.post('/', response_model=Message, status_code=status.HTTP_201_CREATED)
def register_book(user: CurrentUser, book: BookSchema):
    to_register = book.model_dump()
    to_register['user_id'] = user.id

    booksdb.insert_one(to_register)

    return Message(detail='Book added.')


@router.delete('/{book_name}', response_model=Message)
def delete_book(user: CurrentUser, book_name: str):
    res = booksdb.find_one_and_delete({'name': book_name, 'user_id': user.id})

    if not res:
        raise HTTPException(
            detail='Book not found', status_code=status.HTTP_404_NOT_FOUND
        )

    return Message(detail='Book deleted.')
