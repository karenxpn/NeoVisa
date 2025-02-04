from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from order.models import Order
from order.requests import CreateOrderRequest
from user.models import User


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, user: User, model: CreateOrderRequest):
        async with proceed_request(db) as db:
            order = Order(
                credential_id=model.credential_id,
                user_id=user.id,
            )

            db.add(order)
            await db.commit()
            return {
                'success': True,
                'message': 'Order created',
            }
