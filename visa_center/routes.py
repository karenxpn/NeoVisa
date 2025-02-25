from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from user.models import User
from visa_center.requests import AddVisaAccountRequest, UpdateVisaAccountRequest, UpdatePassportRequest
from visa_center.services import VisaCenterService

router = APIRouter()

@router.post('/credentials')
async def add_visa_account(data: AddVisaAccountRequest,
                           current_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.store_visa_center_credentials(db, current_user, data)

@router.get('/credentials/{id}')
async def get_visa_center(id: int,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.get_visa_center_credentials(db, current_user, id)


@router.patch('/credentials/{id}')
async def update_visa_center(id: int,
                             data: UpdateVisaAccountRequest,
                             current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    return await VisaCenterService().update_visa_center_credentials(db, current_user, id, data)


@router.delete('/credentials/{id}')
async def delete_visa_center_credentials(id: int,
                                     current_user: User = Depends(get_current_user),
                                     db: AsyncSession = Depends(get_db)):
    return await VisaCenterService().delete_visa_center_credentials(db, current_user, id)

@router.patch('/passports/{passport_id}')
async def update_passport(passport_id: int,
                          data: UpdatePassportRequest,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.update_passport_detail(db, current_user, passport_id, data)

