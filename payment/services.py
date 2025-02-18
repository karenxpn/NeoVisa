import json
import os
import aiohttp
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from payment.requests import GatewayRequest
from user.models import User
from ulid import ULID


class PaymentService:

    def __init__(self):
        self.base_url = os.environ.get("PAYMENT_BASE_URL")
        self.username = os.environ.get("PAYMENT_USERNAME")
        self.password = os.environ.get("PAYMENT_PASSWORD")

        print('credentials', self.base_url, self.username, self.password)

    async def receive_payment_gateway(self, db: AsyncSession, user: User, model: GatewayRequest = None):
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
            print('requesting url', url)
            headers = {
                'Content-Type': 'application/json',  # Set Content-Type header to application/json
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, ssl=False) as response:
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
