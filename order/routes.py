from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user

from core.database import get_db
from core.jwt_token import get_current_user
from order.requests import CreateOrderRequest
from order.services import OrderService
from user.models import User

router = APIRouter()

@router.post("/orders")
async def create_order(data: CreateOrderRequest,
                       user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    return await OrderService.create_order(db, user, data)


@router.get("/orders/{order_id}")
async def get_order(order_id: int,
                    user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):

    return await OrderService.get_order(order_id, db, user)