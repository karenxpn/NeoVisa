from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from user.models import User
from visa_center.models.visa_center_model import VisaCenterCredentials
from visa_center.requests import AddVisaAccountRequest
from visa_center.spain.automation.authentication import BLSAuthentication


class VisaCenterService:
    @staticmethod
    async def store_visa_center_credentials(db: AsyncSession, user: User, credentials: AddVisaAccountRequest):
        async with proceed_request(db) as db:
            visa_account = VisaCenterCredentials(
                username = credentials.username,
                user_id = user.id,
            )
            visa_account.set_password(credentials.password)

            db.add(visa_account)
            await db.commit()

            return {
                'success': True,
                "message": "Visa account added successfully"
            }

    @staticmethod
    async def run_visa_authentication(credentials: VisaCenterCredentials):
        service = BLSAuthentication(credentials.username, credentials.get_password())
        await service.login()