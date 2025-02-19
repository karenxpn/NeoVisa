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

    async def create_order(self, db: AsyncSession, user: User, model: CreateOrderRequest):
        async with proceed_request(db) as db:
            visa_credentials = await self.get_visa_credentials(db, model.credential_id, user, True)
            print('visa_credentials', visa_credentials)

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

            user_default_payment = await self.get_user_card(db, user, model.card_id)
            print('user default payment method', user_default_payment)
            print('payment order id = ', payment_order['orderId'])
            print('user binding id = ', user_default_payment.binding_id)

            payment_process = await PaymentService().perform_binding_payment(payment_order['orderId'],
                                                                             user_default_payment.binding_id)
            print(payment_process)

            await db.commit()

            await send_task(str(order.id), json.dumps(order_data), topic=topic)

            return {
                'success': True,
                'message': 'Order created',
            }

    @staticmethod
    async def get_user_card(db: AsyncSession, user: User, card_id: int = None):
        async with proceed_request(db) as db:
            query = select(Card).where(Card.user_id == user.id)

            if card_id is not None:
                query = query.where(Card.id == card_id)
            else:
                query = query.where(Card.default_card == True)

            user_card = await db.execute(query)
            user_card = user_card.scalar_one_or_none()

            if user_card is None:
                raise HTTPException(status_code=404, detail="User Default Payment not found")

            return user_card

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

            print('order now', )

            if not result:
                raise Exception('Order not found')

            order.status = status
            await db.commit()

    @staticmethod
    async def get_visa_credentials(db: AsyncSession, credentials_id: int, user: User, load_passports: bool = False):
        query = select(VisaCenterCredentials).where(VisaCenterCredentials.id == credentials_id)

        if load_passports:
            query = query.options(selectinload(VisaCenterCredentials.passports))

        result = await db.execute(query)
        visa_credentials = result.scalar_one_or_none()

        print('visa_credentials inside', visa_credentials)

        if visa_credentials is None:
            raise HTTPException(status_code=404, detail="Visa Center Credentials not found")

        if user and visa_credentials.user_id != user.id:
            raise HTTPException(status_code=403, detail="User ID mismatch")

        return visa_credentials

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

