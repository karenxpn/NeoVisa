from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from core.database import Base

class PhoneOtp(Base):
    __tablename__ = "phone_otps"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, unique=True)
    otp = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    token = Column(String, index=True)