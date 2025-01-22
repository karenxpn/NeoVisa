import datetime
import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import PhoneOtp, Token
from auth.requests import PhoneNumberRequest, OTPRequest
from jwt_token import create_access_token
from proceed_request import proceed_request
from user.models import User


async def send_otp(data: PhoneNumberRequest, db: AsyncSession):
    async with proceed_request(db) as db:
        existing_user = await db.execute(select(User).where(User.phone_number == data.phone_number))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            user = User(
                phone_number=data.phone_number,
                username=f"user_{data.phone_number}",
            )
            db.add(user)

        gen_otp = str(random.randint(100000, 999999))

        existing_otp = await db.execute(select(PhoneOtp).where(PhoneOtp.phone_number == data.phone_number))
        existing_otp = existing_otp.scalar_one_or_none()

        if existing_otp:
            existing_otp.otp = gen_otp
        else:
            otp = PhoneOtp(phone_number=data.phone_number, otp=gen_otp)
            db.add(otp)

        await db.commit()
        return {
            'success': True,
            'otp': gen_otp,
        }


async def verify_otp(data: OTPRequest, db: AsyncSession):
    async with proceed_request(db) as db:
        result = await db.execute(select(PhoneOtp).where(PhoneOtp.phone_number == data.phone_number))
        otp = result.scalars().first()

        if otp is None:
            raise HTTPException(status_code=404, detail="OTP not found")

        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        expiration_time = otp.created_at.replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=10)

        if current_time > expiration_time:
            await db.delete(otp)
            await db.commit()
            raise HTTPException(status_code=400, detail="OTP expired")

        if data.otp != str(otp.otp):
            raise HTTPException(status_code=400, detail="OTP does not match")

        result = await db.execute(select(User).where(User.phone_number == data.phone_number))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verified = True

        access_token = create_access_token(
            data={'sub': data.phone_number},
        )

        token = Token(token=access_token, user_id=user.id)
        db.add(token)

        await db.delete(otp)
        await db.commit()

        return {
            'token': access_token,
        }


