from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy import sql as sa


from core.database import Base

class PhoneOtp(Base):
    __tablename__ = "phone_otps"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, unique=True)
    otp = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    token = Column(String, index=True)