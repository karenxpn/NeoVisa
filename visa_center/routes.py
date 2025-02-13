from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from user.models import User
from visa_center.requests import AddVisaAccountRequest, UpdateVisaAccountRequest
from visa_center.services import VisaCenterService

router = APIRouter()

@router.post('/visa-center')
async def add_visa_account(data: AddVisaAccountRequest,
                           current_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.store_visa_center_credentials(db, current_user, data)

@router.get('/visa-center/{id}')
async def get_visa_center(id: int,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    return await VisaCenterService.get_visa_center_credentials(db, current_user, id)


@router.patch('/visa-center/{id}')
async def update_visa_center(id: int,
                             data: UpdateVisaAccountRequest,
                             current_user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    return await VisaCenterService().update_visa_center_credentials(db, current_user, id, data)


@router.delete('/visa-center/{id}')
async def delete_visa_center_credentials(id: int,
                                     current_user: User = Depends(get_current_user),
                                     db: AsyncSession = Depends(get_db)):
    return await VisaCenterService().delete_visa_center_credentials(db, current_user, id)

