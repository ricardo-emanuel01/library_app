from fastapi import APIRouter

from library_app.database import notifications
from library_app.schemas import Notification
from library_app.routes.utils import CurrentUser, Limit, Skip

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/', response_model=list[Notification])
def get_notifications(user: CurrentUser, limit: Limit = 10, skip: Skip = 0):
    current_notifications = list(notifications.find({'user_id': user.id}))
    return current_notifications
