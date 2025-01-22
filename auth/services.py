import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import PhoneOtp
from auth.requests import PhoneNumberRequest
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