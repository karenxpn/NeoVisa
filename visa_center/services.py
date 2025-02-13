from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.proceed_request import proceed_request
from user.models import User
from visa_center.models import VisaCenterCredentials, Passport
from visa_center.requests import AddVisaAccountRequest, VisaAccountCredentialsResponse, UpdateVisaAccountRequest
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
    async def get_visa_center_credentials_with_id(db: AsyncSession, user: User, cred_id: int):
        result = await db.execute(
            select(VisaCenterCredentials)
            .where(VisaCenterCredentials.id == cred_id)
        )

        visa_account = result.scalar_one_or_none()

        if not visa_account:
            raise HTTPException(status_code=404, detail="Visa account not found")

        if visa_account.user_id != user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

        return visa_account


    async def delete_visa_center_credentials(self, db: AsyncSession, user: User, cred_id: int):
        async with proceed_request(db) as db:
            visa_account = await self.get_visa_center_credentials_with_id(db, user, cred_id)

            await db.delete(visa_account)
            await db.commit()

            return {"success": True, "message": "Visa account deleted successfully"}

    @staticmethod
    async def get_visa_center_credentials(db: AsyncSession, user: User, cred_id: int):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(VisaCenterCredentials)
                .options(selectinload(VisaCenterCredentials.passports))
                .where(VisaCenterCredentials.id == cred_id)
            )

            visa_account = result.scalar_one_or_none()

            if not visa_account:
                raise HTTPException(status_code=404, detail="Visa account not found")

            if visa_account.user_id != user.id:
                raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

            return VisaAccountCredentialsResponse.model_validate(visa_account)

    async def update_visa_center_credentials(self, db: AsyncSession, user: User, id: int, credentials: UpdateVisaAccountRequest):
        async with proceed_request(db) as db:
            visa_account = await self.get_visa_center_credentials_with_id(db, user, id)

            update_dict = credentials.model_dump(exclude_unset=True, exclude={'password', 'passports'})
            for key, value in update_dict.items():
                setattr(visa_account, key, value)

            await db.commit()

            visa_account_dict = visa_account.__dict__.copy()
            visa_account_dict.pop('encrypted_password')
            return visa_account_dict



    @staticmethod
    async def run_visa_authentication(credentials: VisaCenterCredentials):
        service = BLSAuthentication(credentials.username, credentials.get_password())
        await service.login()