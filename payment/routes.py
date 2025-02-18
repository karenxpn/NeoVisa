from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from payment.requests import GatewayRequest
from payment.services import PaymentService
from user.models import User

router = APIRouter()

@router.get("/gateway")
async def create_order(data: GatewayRequest = Body(None),
                       user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    return await PaymentService().receive_payment_gateway(db, user, data)
