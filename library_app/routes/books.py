from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from library_app.database import booksdb
from library_app.models import User
from library_app.schemas import BookPublic, BookSchema, Message
from library_app.security import get_current_user

router = APIRouter(prefix='/book', tags=['book'])


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_model=list[BookPublic])
def get_books_user(
    user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 10,
):
    books = list(booksdb.find({'user_id': user.id}, skip=skip, limit=limit))

    if not books:
        raise HTTPException(
            detail='not found', status_code=status.HTTP_404_NOT_FOUND
        )

    for book in books:
        str_id = str(book['_id'])
        book.pop('_id')
        book['id'] = str_id

    return books


@router.get('/books', response_model=list[BookPublic])
def get_books(
    type: Annotated[str, Query(max_length=3)] = 'or',
    genres: Annotated[list[str] | None, Query()] = None,
    book_name: Annotated[str | None, Query(max_length=50)] = None,
    author: Annotated[str | None, Query(max_length=30)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 10,
):
    query = {}
    if genres:
        if len(query) == 0:
            query[f'${type}'] = []
        
        for genre in genres:
            query[f'${type}'].append({'genre': genre})

    if book_name:
        if len(query) == 0:
            query[f'${type}'] = []

        query[f'${type}'].append({'name': {'$regex': book_name}})

    if author:
        if len(query) == 0:
            query[f'${type}'] = []

        query[f'${type}'].append({'author': {'$regex': author}})

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
