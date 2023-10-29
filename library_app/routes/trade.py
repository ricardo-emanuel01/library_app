from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from library_app.database import booksdb, trades
from library_app.routes.utils import CurrentUser, Limit, Skip, OfferId
from library_app.schemas import Message, Trade, TradeViwer, StatusTrade

router = APIRouter(prefix='/trade', tags=['trade'])


@router.get('/', response_model=list[TradeViwer])
def get_trade_offers(user: CurrentUser, skip: Skip = 0, limit: Limit = 10):
    query = {'$or': [{'sender_id': user.id}, {'receiver_id': user.id}]}

    trade_offers = list(trades.find(query, skip=skip, limit=limit))

    for offer in trade_offers:
        str_id = str(offer['_id'])
        offer.pop('_id')
        offer['id'] = str_id

    return trade_offers


@router.post('/', response_model=Message)
def post_trade_offer(user: CurrentUser, trade: Trade):
    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Book not found.',
    )

    trade_offer = trade.model_dump()

    query_requested = {
        '$and': [
            {'user_id': trade_offer['receiver_id']},
            {'name': {'$regex': trade_offer['book_requested']}},
        ]
    }
    book_requested = booksdb.find_one(query_requested)
    if not book_requested:
        raise not_found_exception

    query_offered = {
        '$and': [
            {'user_id': user.id},
            {'name': {'$regex': trade_offer['book_offered']}},
        ]
    }
    book_offered = booksdb.find_one(query_offered)
    if not book_offered:
        raise not_found_exception

    now = datetime.now()
    trade_offer['status'] = StatusTrade.awaiting_approval
    trade_offer['sender_id'] = user.id
    trade_offer['year'] = now.year
    trade_offer['month'] = now.month
    trade_offer['day'] = now.day
    trade_offer['hour'] = now.hour

    trades.insert_one(trade_offer)

    return Message(detail='Trade offer sended.')


@router.delete('/', response_model=Message)
def delete_trade_offer(user: CurrentUser, offer_id: OfferId):
    id = ObjectId(offer_id)
    to_delete = trades.find_one({'_id': id})
    if to_delete:
        if (
            to_delete['receiver_id'] == user.id
            or to_delete['sender_id'] == user.id
        ):
            trades.delete_one({'_id': id})
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Not enough permissions.',
            )

    return Message(detail='Trade deleted.')
