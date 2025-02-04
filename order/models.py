from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Relationship
from sqlalchemy import Enum as SQLEnum
from enum import Enum

from core.database import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)

    credential_id = Column(Integer, ForeignKey("visa_center_credentials.id", ondelete="CASCADE"), nullable=False)
    visa_credentials = Relationship('VisaCenterCredentials', back_populates="orders")

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    user = Relationship('User', back_populates='orders')


    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))


