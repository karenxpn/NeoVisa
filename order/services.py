import json

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from order.models import Order
from order.requests import CreateOrderRequest, UpdateOrderRequest
from user.models import User
from visa_center.models import VisaCenterCredentials
from core.kafka_producer import send_task


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, user: User, model: CreateOrderRequest):
        async with proceed_request(db) as db:

            visa_credentials = await db.execute(
                select(VisaCenterCredentials)
                .where(VisaCenterCredentials.id == model.credential_id)
            )
            visa_credentials = visa_credentials.scalar_one_or_none()

            if visa_credentials is None:
                raise HTTPException(status_code=404, detail="Visa Center Credentials not found")

            if visa_credentials.user_id != user.id:
                raise HTTPException(status_code=403, detail="User ID mismatch")

            order = Order(
                credential_id=model.credential_id,
                user_id=user.id,
            )

            db.add(order)
            await db.commit()


            print('Orderid: ', order.id)

            order_data = {
                'order_id': order.id,
                'status': order.status,
                'user_id': user.id,
                'visa_credentials': {
                    'id': visa_credentials.id,
                    'username': visa_credentials.username,
                    'password': visa_credentials.get_password()
                },
            }

            send_task(str(order.id), order_data)

            print(order_data)

            return {
                'success': True,
                'message': 'Order created',
            }

    @staticmethod
    async def get_order(order_id: int, db: AsyncSession, user: User):
        async with proceed_request(db) as db:
            order = await db.execute(
                select(Order).where(Order.id == order_id)
            )

            order = order.scalars().first()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if order.user_id != user.id:
                raise HTTPException(status_code=403, detail="You do not have permission to access this order")

            return order

    @staticmethod
    async def get_orders(db: AsyncSession, user: User):
        async with proceed_request(db) as db:
            orders = await db.execute(
                select(Order).where(Order.user_id == user.id)
            )

            return orders.scalars().all()


    @staticmethod
    async def update_order(order_id: int, db: AsyncSession, user: User, model: UpdateOrderRequest):
        async with proceed_request(db) as db:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalars().first()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if order.user_id != user.id:
                raise HTTPException(status_code=403, detail="You do not have permission to update this order")

            order.status = model.status
            await db.commit()
            await db.refresh(order)
            return order


