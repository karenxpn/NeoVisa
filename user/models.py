from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    phone_number = Column(String, index=True, unique=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))