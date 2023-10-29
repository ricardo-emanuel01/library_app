from fastapi import APIRouter, HTTPException, status

from library_app.database import booksdb
from library_app.query_builder import query_builder
from library_app.routes.utils import (
    Author,
    BookName,
    CurrentUser,
    Genre1,
    Genre2,
    Limit,
    Skip,
    Type,
    UserId,
)
from library_app.schemas import (
    BookPublic,
    BookPublicUnauthenticated,
    BookSchema,
    Message,
)

router = APIRouter(prefix='/book', tags=['book'])


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

    if books:
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

    if books:
        for book in books:
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
