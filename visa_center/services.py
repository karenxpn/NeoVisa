from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from user.models import User
from visa_center.models import VisaCenterCredentials, Passport
from visa_center.requests import AddVisaAccountRequest
from visa_center.spain.automation.authentication import BLSAuthentication


class VisaCenterService:
    @staticmethod
    async def store_visa_center_credentials(db: AsyncSession, user: User, credentials: AddVisaAccountRequest):
        async with proceed_request(db) as db:
            visa_account_data = credentials.model_dump(exclude={'passports', 'password'})
            visa_account_data['user_id'] = user.id

            visa_account = VisaCenterCredentials(**visa_account_data)
            visa_account.set_password(credentials.password)

            db.add(visa_account)
            await db.flush()

            if credentials.passports:
                passport_entries = [
                    Passport(
                        **passport.model_dump(),
                        credentials_id=visa_account.id
                    )
                    for passport in credentials.passports
                ]

                db.add_all(passport_entries)

            await db.commit()

            return {
                'success': True,
                "message": "Visa account added successfully"
            }

    @staticmethod
    async def delete_visa_center_credentials(db: AsyncSession, user: User, account_id: int):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(VisaCenterCredentials)
                .where(VisaCenterCredentials.id == account_id)
            )

            visa_account = result.scalar_one_or_none()

            if not visa_account:
                raise HTTPException(status_code=404, detail="Visa account not found")

            await db.delete(visa_account)
            await db.commit()

            return {"success": True, "message": "Visa account deleted successfully"}


    @staticmethod
    async def run_visa_authentication(credentials: VisaCenterCredentials):
        service = BLSAuthentication(credentials.username, credentials.get_password())
        await service.login()