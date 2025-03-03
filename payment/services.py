import json
import os
import aiohttp
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request, network_request
from payment.models import Card
from payment.requests import GatewayRequest, AttachCardRequest, CardCreate, CardResponse
from user.models import User
from ulid import ULID



class PaymentService:

    def __init__(self):
        self.base_url = os.environ.get("PAYMENT_BASE_URL")
        self.username = os.environ.get("PAYMENT_USERNAME")
        self.password = os.environ.get("PAYMENT_PASSWORD")

    async def receive_payment_gateway(self, user: User, model: GatewayRequest = None):

        amount = model.amount if model is not None else 10
        order_number = str(ULID())

        url = f"{self.base_url}/register.do"

        params = {
            "userName": self.username,
            "password": self.password,
            "orderNumber": order_number,
            "returnUrl": "https://neovisa.am",
            "amount": amount,
            "clientId": user.id,
            "currency": '051',
        }

        async with network_request() as session:
            async with session.get(url, params=params, ssl=False) as response:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    raw_response = await response.text()
                    data = json.loads(raw_response)

                data['orderNumber'] = order_number

                if data.get('error'):
                    raise HTTPException(status_code=500, detail=data.get('errorMessage', ""))

                return data


    async def attach_card(self, db: AsyncSession, user: User, model: AttachCardRequest):
        order_id = model.order_id
        order_number = model.order_number

        data = await self.check_order_status(order_id, order_number)

        async with proceed_request(db) as db:
            card_data = await CardCreate.from_response(data, user.id, data.bindingInfo.bindingId, db)
            card = Card(**card_data.model_dump())

            db.add(card)
            await db.commit()

            return {
                'success': True,
                'message': 'Your card was successfully added'
            }

    @staticmethod
    async def get_payment_method(db, user, card_id):
        result = await db.execute(
            select(Card)
            .where(Card.id == card_id)
        )

        card = result.scalar_one_or_none()
        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")

        if card.user_id != user.id:
            raise HTTPException(status_code=403, detail='Your are not the owner of this card')

        return card


    async def get_payment_method_by_id(self, db: AsyncSession, user: User, card_id: int):
        async with proceed_request(db) as db:
            card = await self.get_payment_method(db, user, card_id)

            return card

    async def get_payment_methods_list(self, db: AsyncSession, user: User):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(Card)
                .where(Card.user_id == user.id)
            )
            cards = result.scalars().all()

            return cards

    async def remove_payment_method(self, db: AsyncSession, user: User, card_id: int):
        async with proceed_request(db) as db:
            card = await self.get_payment_method(db, user, card_id)
            await db.delete(card)
            await db.commit()

            return {
                'success': True,
                'message': 'Your card was successfully deleted.'
            }

    async def check_order_status(self, order_number, order_id):
        url = f"{self.base_url}/getOrderStatusExtended.do"
        params = {
            'userName': self.username,
            'password': self.password,
            'orderNumber': order_number,
            'orderId': order_id,
        }

        async with network_request() as session:
            async with session.get(url, params=params, ssl=False) as response:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    raw_response = await response.text()
                    data = json.loads(raw_response)

                data = CardResponse(**data)
                return data


    async def perform_binding_payment(self, md_order: str, binding_id: str):
        url = f'{self.base_url}/paymentOrderBinding.do'
        params = {
            'userName': self.username,
            'password': self.password,
            'mdOrder': md_order,
            'bindingId': binding_id,
            'cvc': '000'
        }

        async with network_request() as session:
            async with session.post(url, params=params, ssl=False) as response:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    raw_response = await response.text()
                    data = json.loads(raw_response)

                if data.get('success', None) is not None and data.get('success', None) != 0:
                    raise HTTPException(status_code=500, detail=data['info'])
                if data.get('errorCode', None):
                    raise HTTPException(status_code=500, detail=data['error'])

                return data

    async def update_default_card(self, db: AsyncSession, user: User, card_id: int):
        async with proceed_request(db) as db:
            card = await self.get_payment_method(db, user, card_id)
            card.default_card = True

            await db.execute(
                update(Card)
                .where(Card.user_id == user.id, Card.id != card_id)
                .values(default_card=False)
            )

            await db.commit()

            return {
                'success': True,
                'message': 'Your default card was successfully updated.'
            }
