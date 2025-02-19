import json

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.proceed_request import proceed_request
from order.models import Order, OrderStatus
from order.order_serializer import OrderSerializer
from order.requests import CreateOrderRequest, UpdateOrderRequest
from payment.models import Card
from payment.requests import GatewayRequest
from payment.services import PaymentService
from user.models import User
from visa_center.models import VisaCenterCredentials, CountryEnum
from core.kafka_producer import send_task


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, user: User, model: CreateOrderRequest):
        async with proceed_request(db) as db:

            visa_credentials = await db.execute(
                select(VisaCenterCredentials)
                .options(selectinload(VisaCenterCredentials.passports))
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
            await db.flush()


            print('Orderid: ', order.id)
            order_data = OrderSerializer.model_validate(order)
            order_data = jsonable_encoder(order_data)

            match visa_credentials.country:
                case CountryEnum.ES:
                    topic = 'visa-es-orders'
                case CountryEnum.GR:
                    topic = 'visa-gr-orders'


            gateway_request = GatewayRequest(
                amount=visa_credentials.passports_count * 3000
            )

            payment_order = await PaymentService().receive_payment_gateway(user, gateway_request)
            print(payment_order)
            print('payment order type', type(payment_order))

            user_default_payment = await db.execute(
                select(Card)
                .where(Card.user_id == user.id)
                .where(Card.default_card == True)
            )

            user_default_payment = user_default_payment.scalar_one_or_none()
            if user_default_payment is None:
                raise HTTPException(status_code=404, detail="User Default Payment not found")

            print('user default payment method', user_default_payment)
            print('payment order id = ', payment_order['orderId'])
            print('user binding id = ', user_default_payment.binding_id)

            payment_process = await PaymentService().perform_binding_payment(payment_order['orderId'],
                                                                             user_default_payment.binding_id)
            print(payment_process)

            await PaymentService().receive_payment_gateway(user, )

            await send_task(str(order.id), json.dumps(order_data), topic=topic)

            await db.commit()
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

