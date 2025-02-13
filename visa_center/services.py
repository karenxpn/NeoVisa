from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from core.proceed_request import proceed_request
from order.models import Order, OrderStatus
from user.models import User
from visa_center.models import VisaCenterCredentials, Passport
from visa_center.requests import AddVisaAccountRequest, VisaAccountCredentialsResponse, UpdateVisaAccountRequest, \
    UpdatePassportRequest, VisaAccountPassport
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
                        credentials_id=visa_account.id,
                        user_id=user.id
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

            visa_account_passports = [
                VisaAccountPassport(**passport.__dict__) for passport in visa_account.passports
            ]

            return VisaAccountCredentialsResponse(
                id=visa_account.id,
                country=visa_account.country,
                username=visa_account.username,
                user_id=visa_account.user_id,
                passports=visa_account_passports
            )


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
    async def update_passport_detail(db: AsyncSession, user: User, passport_id: int, details: UpdatePassportRequest):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(Passport)
                .where(Passport.id == passport_id)
            )

            passport = result.scalar_one_or_none()

            if not passport:
                raise HTTPException(status_code=404, detail="Passport not found")

            if passport.user_id != user.id:
                raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

            # check if there is an order with the passport that is PROCESSING
            visa_credentials_alias = aliased(VisaCenterCredentials)

            order = await db.execute(
                select(Order)
                .join(visa_credentials_alias, visa_credentials_alias.id == Order.credential_id)
                .join(Passport, Passport.credentials_id == visa_credentials_alias.id)
                .where(Passport.id == passport_id)
                .where(Order.status == OrderStatus.PROCESSING)
            )

            order = order.scalar_one_or_none()

            if order:
                raise HTTPException(403, 'Order is being processed with this passport, you are not authorized to perform this action')

            update_dict = details.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(passport, key, value)

            await db.commit()
            return passport



    @staticmethod
    async def run_visa_authentication(credentials: VisaCenterCredentials):
        service = BLSAuthentication(credentials.username, credentials.get_password())
        await service.login()