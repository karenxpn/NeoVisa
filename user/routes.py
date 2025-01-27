from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from main import security
from user.services import get_user_by_id, get_user

router = APIRouter()

# this should be allowed to the admins
@router.get('/users/{user_id}')
async def get_user_by_id_route(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
    return await get_user_by_id(user_id, db, credentials)

@router.get('/user')
async def get_user_route(
        db: AsyncSession = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await get_user(db, credentials)