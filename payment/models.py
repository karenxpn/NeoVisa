from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime


from core.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(32), nullable=False, index=True)
    expiration_date = Column(String, nullable=False, index=True)
    card_holder_name = Column(String, nullable=False, index=True)
    bank_name = Column(String, nullable=True, index=True)
    binding_id = Column(Integer, nullable=False, index=True)

    default_card = Column(Boolean, default=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="cards")

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))
