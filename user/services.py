from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.jwt_token import decode_access_token
from core.proceed_request import proceed_request
from user.models import User


async def get_user_by_id(user_id: int,
                   db: AsyncSession,
                   credentials: HTTPAuthorizationCredentials
                ):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with proceed_request(db) as db:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        return user


async def get_user(db: AsyncSession,
                   credentials: HTTPAuthorizationCredentials):

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    phone_number = payload.get('sub', None)
    if not phone_number:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with proceed_request(db) as db:
        result = await db.execute(select(User).filter(User.phone_number == phone_number))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail=f"User not found")

        return user
