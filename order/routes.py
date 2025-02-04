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
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    return await OrderService.create_order(db, current_user, data)
