from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.requests import PhoneNumberRequest, OTPRequest
from auth.services import send_otp
from database import get_db


router = APIRouter()


@router.post('/send-otp')
async def send_otp_route(data: PhoneNumberRequest, db: AsyncSession = Depends(get_db)):
    return await send_otp(data, db)

