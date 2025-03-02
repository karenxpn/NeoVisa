from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from payment.requests import GatewayRequest, AttachCardRequest
from payment.services import PaymentService
from user.models import User

router = APIRouter()

@router.get("/gateway")
async def create_order(data: GatewayRequest = Body(None),
                       user: User = Depends(get_current_user)):
    return await PaymentService().receive_payment_gateway(user, data)

@router.post("/payment-methods")
async def create_payment_method(data: AttachCardRequest,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    return await PaymentService().attach_card(db, user, data)

@router.get("/payment-methods/{id}")
async def get_payment_method(id: int,
                             user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    return await PaymentService().get_payment_method_by_id(db, user, id)

@router.get('/payment-methods')
async def get_payment_methods(user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    return await PaymentService().get_payment_methods_list(db, user)


@router.delete('/payment-methods/{card_id}')
async def delete_payment_method(card_id: int,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    return await PaymentService().remove_payment_method(db, user, card_id)

@router.post('/payment-methods/default/{card_id}')
async def make_default_payment_method(card_id: int,
                                      user: User = Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    return await PaymentService().update_default_card(db, user, card_id)