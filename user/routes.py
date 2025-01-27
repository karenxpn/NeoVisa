from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.jwt_token import get_current_user
from user.models import User
from user.services import delete_user

router = APIRouter()

@router.get('/user')
async def get_user_route(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete('/user')
async def delete_user_route(current_user: User = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    return await delete_user(current_user, db)