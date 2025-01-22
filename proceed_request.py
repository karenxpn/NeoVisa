from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def proceed_request(db: AsyncSession):
    try:
        yield db
    except SQLAlchemyError as e:
        await db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        raise HTTPException(
            status_code=400,
            detail=f"Database error occurred: {error_msg}"
        )
    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )