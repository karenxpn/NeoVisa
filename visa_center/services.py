from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from core.proceed_request import proceed_request
from order.models import Order, OrderStatus
from order.services import OrderService
from user.models import User
from visa_center.models import VisaCenterCredentials, Passport, VisaCenter
from visa_center.requests import AddVisaAccountCredentialsRequest, VisaAccountCredentialsResponse, \
    UpdateVisaAccountRequest, \
    UpdatePassportRequest, VisaAccountPassport, AddVisaCenterRequest, UpdateVisaCenterRequest
from visa_center.spain.automation.authentication import BLSAuthentication


class VisaCenterService:
    @staticmethod
    async def store_visa_center_credentials(db: AsyncSession, user: User, credentials: AddVisaAccountCredentialsRequest):
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
    async def delete_visa_center_credentials(db: AsyncSession, user: User, cred_id: int):
        async with proceed_request(db) as db:
            visa_account = await OrderService.get_visa_credentials(db, cred_id, user, False)

            await db.delete(visa_account)
            await db.commit()

            return {"success": True, "message": "Visa account deleted successfully"}

    @staticmethod
    async def get_visa_center_credentials(db: AsyncSession, user: User, cred_id: int):
        async with proceed_request(db) as db:
            visa_account = await OrderService.get_visa_credentials(db, cred_id, user, True)

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
            visa_account = await OrderService.get_visa_credentials(db, id, user, False)

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

            order = order.scalars().first()

            if order:
                raise HTTPException(403, 'Order is being processed with this passport, you are not authorized to perform this action')

            update_dict = details.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(passport, key, value)

            await db.commit()
            return passport

    @staticmethod
    async def get_visa_center_list(db: AsyncSession):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(VisaCenter)
            )
            visa_centers = result.scalars().all()

            return visa_centers

    @staticmethod
    async def get_visa_center_by_id(id: int, db: AsyncSession):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(VisaCenter)
                .where(VisaCenter.id == id)
            )

            visa_centers = result.scalar_one_or_none()
            return visa_centers

    @staticmethod
    async def create_visa_center(db: AsyncSession, model: AddVisaCenterRequest):
        async with proceed_request(db) as db:
            visa_center = VisaCenter(**model.model_dump(exclude_unset=True))
            db.add(visa_center)
            await db.commit()

            return visa_center

    @staticmethod
    async def update_visa_center(id: int, db: AsyncSession, model: UpdateVisaCenterRequest):
        async with proceed_request(db) as db:
            result = await db.execute(
                select(VisaCenter)
                .where(VisaCenter.id == id)
            )

            visa_center = result.scalar_one_or_none()

            update_dict = model.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(visa_center, key, value)

            await db.commit()
            return visa_center


    @staticmethod
    async def run_visa_authentication(credentials: VisaCenterCredentials):
        service = BLSAuthentication(credentials.username, credentials.get_password())
        await service.login()