from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.proceed_request import proceed_request
from user.models import User, Email
from user.requests import UpdateUserRequest, update_user_whitelist


class UserService:
    @staticmethod
    async def update_user(db: AsyncSession, user: User, update_model: UpdateUserRequest):
        async with proceed_request(db) as db:
            updates = {field: value for field, value in update_model.model_dump(exclude_unset=True).items() if field in update_user_whitelist}

            for field, value in updates.items():
                setattr(user, field, value)

            # Handle email separately since it's a relationship
            if update_model.email is not None:
                user = await db.execute(
                    select(User).options(selectinload(User.email)).filter_by(id=user.id)
                )
                user = user.scalars().first()

                if user.email:
                    # Update existing email
                    user.email.email = update_model.email
                    user.email.is_verified = False
                    db.add(user.email)
                else:
                    # Create new email
                    new_email = Email(
                        email=str(update_model.email),
                        user_id=user.id,
                        is_verified=False
                    )
                    db.add(new_email)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return {
                'success': True,
                'message': 'User updated successfully.',
            }

    @staticmethod
    async def delete_user(user: User, db: AsyncSession):
        async with proceed_request(db) as db:
            await db.delete(user)
            await db.commit()

            return {
                "status": "success",
                "message": "User deleted",
            }
