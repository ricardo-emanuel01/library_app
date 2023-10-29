from typing import Annotated

from fastapi import APIRouter, Depends, Query

from library_app.database import booksdb
from library_app.models import User
from library_app.schemas import BookPublic
from library_app.security import get_current_user

router = APIRouter(prefix='/timeline', tags=['timeline'])

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_model=list[BookPublic])
def get_timeline(
    user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 10,
):
    genre1 = user.genre1
    genre2 = user.genre2

    query = {
        '$and': [
            {'user_id': {'$ne': user.id}},
            {'$or': [{'genre': genre1}, {'genre': genre2}]},
        ]
    }

    books = list(booksdb.find(query, skip=skip, limit=limit))

    if not books:
        books = list(booksdb.find({}, skip=skip, limit=limit))

    for book in books:
        str_id = str(book['_id'])
        book.pop('_id')
        book['id'] = str_id

    return books
