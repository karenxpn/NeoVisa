from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from user.models import User


async def delete_user(user: User, db: AsyncSession):
    async with proceed_request(db) as db:
        await db.delete(user)
        await db.commit()

        return {
            "status": "success",
            "message": "User deleted",
        }
