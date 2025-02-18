import json
import os
import aiohttp
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from payment.models import Card
from payment.requests import GatewayRequest, AttachCardRequest
from user.models import User
from ulid import ULID



class PaymentService:

    def __init__(self):
        self.base_url = os.environ.get("PAYMENT_BASE_URL")
        self.username = os.environ.get("PAYMENT_USERNAME")
        self.password = os.environ.get("PAYMENT_PASSWORD")

        print('credentials', self.base_url, self.username, self.password)

    async def receive_payment_gateway(self, user: User, model: GatewayRequest = None):
        url = f"{self.base_url}/register.do"

        amount = model.amount if model is not None else 500
        order_number = str(ULID())

        params = {
            "userName": self.username,
            "password": self.password,
            "orderNumber": order_number,
            "returnUrl": "https://neovisa.am/",
            "amount": amount,
            "clientId": user.id,
        }

        print('order_number', order_number)

        try:
            url = f"{self.base_url}/register.do"

            async with aiohttp.ClientSession() as session:
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

        except aiohttp.ClientError as e:
            raise e
        except Exception as e:
            raise e

    async def check_binding_existence(self, db: AsyncSession, user: User, binding_id: str):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(Card)
                .where(Card.user_id == user.id)
                .where(Card.binding_id == binding_id)
            )

            card = result.scalar_one_or_none()
            return card

    async def attach_card(self, db: AsyncSession, user: User, model: AttachCardRequest):
        order_id = model.order_id
        order_number = model.order_number

        try:
            url = f"{self.base_url}/getOrderStatusExtended.do"
            params = {
                'userName': self.username,
                'password': self.password,
                'orderNumber': order_number,
                'orderId': order_id,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, ssl=False) as response:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        raw_response = await response.text()
                        data = json.loads(raw_response)

                    if data.get('error') or data.get('errorCode', 0) != 0:
                        raise HTTPException(status_code=500, detail=data.get('errorMessage', ""))
                    elif data.get('actionCode', 0) != 0:
                        raise HTTPException(status_code=500, detail=data.get('actionCodeDescription', ""))
                    elif not data.get('bindingInfo'):
                        raise HTTPException(status_code=500, detail='Something went wrong, try again later!')


                    existing_card = await self.check_binding_existence(db, user, data['bindingInfo']['bindingId'])
                    print('existing_card', existing_card)

                    if not existing_card:
                        async with proceed_request(db) as db:
                            expiration = data['cardAuthInfo']['expirationDate']
                            card = Card(
                                user_id=user.id,
                                binding_id=data['bindingInfo']['bindingId'],
                                card_number=data['cardAuthInfo']['pan'],
                                card_holder_name=data['cardAuthInfo']['cardholderName'],
                                expiration_date=f"{expiration[:4]}/{expiration[4:]}",
                                bank_name=data['bankInfo']['bankName']
                            )

                            db.add(card)
                            await db.commit()

                            return {
                                'success': True,
                                'message': 'Your card was successfully added'
                            }

        except aiohttp.ClientError as e:
            raise e
        except Exception as e:
            raise e


