import json

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session, get_db
from core.proceed_request import proceed_request
from order.models import Order, OrderStatus
from order.order_serializer import OrderSerializer
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
            order_data = OrderSerializer.model_validate(order)
            order_data = jsonable_encoder(order_data)
            send_task(str(order.id), json.dumps(order_data))

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
    async def update_order_status(order_id: int, status: OrderStatus):
        async for db in get_db():
            result = await db.execute(
                select(Order)
                .where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()

            if not result:
                raise Exception('Order not found')

            order.status = status
            await db.commit()

    @staticmethod
    async def get_visa_credentials(credentials_id: int):
        async for db in get_db():
            result = await db.execute(
                select(VisaCenterCredentials)
                .where(VisaCenterCredentials.id == credentials_id)
            )
            return result.scalar_one_or_none()

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

