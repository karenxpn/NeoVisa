from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from user.models import User
from visa_center.requests import AddVisaAccountRequest
from visa_center.services import VisaCenterService

router = APIRouter()

@router.post('/visa-center')
async def add_visa_account(data: AddVisaAccountRequest,
                           current_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.store_visa_center_credentials(db, current_user, data)

