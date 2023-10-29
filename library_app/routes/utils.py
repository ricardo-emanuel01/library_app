from typing import Annotated

from fastapi import Depends, Query

from library_app.models import User
from library_app.security import get_current_user

CurrentUser = Annotated[User, Depends(get_current_user)]
Type = Annotated[str, Query(max_length=3, alias='type of filter')]
UserId = Annotated[int | None, Query(ge=1, alias='user id')]
Genre1 = Annotated[str | None, Query(max_length=15, alias='genre')]
Genre2 = Annotated[str | None, Query(max_length=15, alias='second genre')]
BookName = Annotated[str | None, Query(max_length=50, alias='title')]
Author = Annotated[str | None, Query(max_length=30, alias='author name')]
Skip = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1)]
OfferId = Annotated[str, Query()]
