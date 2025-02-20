from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
    return await OrderService().create_order(db, user, data)


@router.get("/orders/{order_id}")
async def get_order(order_id: int,
                    user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):

    return await OrderService.get_order(order_id, db, user)

@router.get("/orders")
async def get_orders(user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    return await OrderService.get_orders(db, user)


### the update should be automated no user can change the status of the order
# @router.patch("/orders/{order_id}")
# async def update_order(order_id: int,
#                        data: UpdateOrderRequest,
#                        user: User = Depends(get_current_user),
#                        db: AsyncSession = Depends(get_db)):
#     return await OrderService.update_order(order_id, db, user, data)