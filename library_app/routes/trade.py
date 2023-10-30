from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, status

from library_app.database import booksdb, notifications, trades
from library_app.routes.utils import (
    build_trade_offer,
    CurrentUser,
    Limit,
    Skip,
    OfferId,
)
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

    trade_offer_complete = build_trade_offer(user.id, trade_offer)

    new_trade = trades.insert_one(trade_offer_complete)
    notification = {
        'user_id': trade.receiver_id,
        'trade_id': str(new_trade.inserted_id),
        'new_status': StatusTrade.awaiting_approval,
    }

    notifications.insert_one(notification)

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


@router.put('/cancel', response_model=Message)
def cancel_trade_offer(user: CurrentUser, offer_id: OfferId):
    id = ObjectId(offer_id)
    query = {'_id': id, 'sender_id': user.id}
    to_cancel = trades.find_one(query)
    if not to_cancel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Trade offer not found.',
        )

    trades.update_one(query, {'$set': {'status': 'canceled'}})
    # Notificar a pessoa que recebeu a oferta

    return Message(detail='Trade offer canceled.')


@router.put('/decline', response_model=Message)
def decline_trade_offer(user: CurrentUser, offer_id: OfferId):
    id = ObjectId(offer_id)
    query = {'_id': id, 'receiver_id': user.id}
    to_decline = trades.find_one(query)
    if not to_decline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Trade offer not found.',
        )

    trades.update_one(query, {'$set': {'status': 'declined'}})
    # Notificar a pessoa que enviou a oferta

    return Message(detail='Trade offer declined.')


@router.put('/accept', response_model=Message)
def accept_trade_offer(user: CurrentUser, offer_id: OfferId):
    id = ObjectId(offer_id)
    query = {'_id': id, 'receiver_id': user.id}
    to_approve = trades.find_one(query)
    if not to_approve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Trade offer not found.',
        )

    trades.update_one(query, {'$set': {'status': 'accepted'}})
    # Notificar a pessoa que enviou a oferta

    return Message(detail='Trade offer accepted.')


@router.put('/', response_model=TradeViwer)
def update_trade_offer(
    user: CurrentUser,
    offer_id: OfferId,
    update_to: Annotated[StatusTrade, Query()],
):
    if update_to == StatusTrade.awaiting_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot update to that.',
        )

    id = ObjectId(offer_id)
    query = {'_id': id}
    notification = {'new_status': update_to}
    if update_to == StatusTrade.canceled:
        query['sender_id'] = user.id
        notification['user_id'] = 'receiver'
    else:
        query['receiver_id'] = user.id
        notification['user_id'] = 'sender'

    print(query)
    offer = trades.find_one(query)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Trade offer not found.',
        )

    notification['trade_id'] = str(offer['_id'])
    if notification['user_id'] == 'sender':
        notification['user_id'] = offer['sender_id']
    else:
        notification['user_id'] = offer['receiver_id']

    trades.update_one(query, {'$set': {'status': update_to}})
    notifications.insert_one(notification)

    to_return = trades.find_one(query)
    to_return['id'] = str(to_return['_id'])
    to_return.pop('_id')

    return to_return
