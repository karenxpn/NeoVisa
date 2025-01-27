from sqlalchemy.ext.asyncio import AsyncSession

from core.proceed_request import proceed_request
from user.models import User
from user.requests import UpdateUserRequest


class UserService:
    @staticmethod
    async def update_user(db: AsyncSession, user: User, update_model: UpdateUserRequest):
        async with proceed_request(db) as db:
            valid_fields = {column.name for column in User.__table__.columns}
            updates = {field: value for field, value in update_model.model_dump(exclude_unset=True).items() if field in valid_fields}

            for field, value in updates.items():
                setattr(user, field, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return user

    @staticmethod
    async def delete_user(user: User, db: AsyncSession):
        async with proceed_request(db) as db:
            await db.delete(user)
            await db.commit()

            return {
                "status": "success",
                "message": "User deleted",
            }
