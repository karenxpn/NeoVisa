from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.requests import PhoneNumberRequest, OTPRequest
from auth.services import send_otp, verify_otp
from core.database import get_db


router = APIRouter()


@router.post('/send-otp')
async def send_otp_route(data: PhoneNumberRequest, db: AsyncSession = Depends(get_db)):
    return await send_otp(data, db)

@router.post('/verify-otp')
async def verify_otp_route(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    return await verify_otp(data, db)
