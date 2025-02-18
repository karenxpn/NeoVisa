import json
import os
import aiohttp
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from payment.models import Card
from payment.requests import GatewayRequest, AttachCardRequest, CardCreate, CardResponse
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

    @staticmethod
    async def check_binding_existence(db: AsyncSession, user: User, binding_id: str):
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

                    data = CardResponse(**data)

                    print('data', data)

                    if data.error and data.errorCode != 0:
                        print('Entered error Code', data.errorMessage)
                        raise HTTPException(status_code=500, detail=data.errorMessage or "")
                    elif data.actionCode != 0:
                        print('Entered actionCode', data.actionCodeDescription)
                        raise HTTPException(status_code=500, detail=data.actionCodeDescription or "")
                    elif not data.bindingInfo:
                        print('No binding info')
                        raise HTTPException(status_code=500, detail='Something went wrong, try again later!')


                    existing_card = await self.check_binding_existence(db, user, data.bindingInfo.bindingId)
                    print('existing_card', existing_card)

                    if not existing_card:
                        async with proceed_request(db) as db:
                            card_data = CardCreate.from_response(data, user.id)
                            card = Card(**card_data.model_dump())

                            db.add(card)
                            await db.commit()

                            return {
                                'success': True,
                                'message': 'Your card was successfully added'
                            }
                    raise HTTPException(status_code=400, detail='This card is already in use.')

        except aiohttp.ClientError as e:
            raise e
        except Exception as e:
            raise e

    @staticmethod
    async def remove_payment_method(db: AsyncSession, user: User, card_id: int):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(Card)
                .where(Card.id == card_id)
            )

            card = result.scalar_one_or_none()
            if card is None:
                raise HTTPException(status_code=404, detail="Card not found")

            if card.user_id != user.id:
                raise HTTPException(status_code=403, detail='Your are not the owner of this card')

            await db.delete(card)
            await db.commit()

            return {
                'success': True,
                'message': 'Your card was successfully deleted.'
            }


