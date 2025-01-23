from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def proceed_request(db: AsyncSession):
    try:
        yield db
    except SQLAlchemyError as e:
        await db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Database error: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Database error occurred: {error_msg}"
        )
    except HTTPException as e:
        await db.rollback()
        logger.warning(f"HTTP exception occurred: {str(e.detail)}")
        raise e
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )