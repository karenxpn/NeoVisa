from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Relationship

from core.database import Base
from enum import Enum as PyEnum
from sqlalchemy import Enum



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    phone_number = Column(String, index=True, unique=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    passport = Relationship('Passport', back_populates='user', passive_deletes=True)


class PassportType(PyEnum):
    ORDINARY = "Ordinary"
    DIPLOMATIC = "Diplomatic"
    COLLECTIVE = "Collective"
    SERVICE = "Service"
    OFFICIAL = "Official"
    FOREIGNERS = 'Passport of foreigners'
    PROTECTION = "Protection passport"
    UN = 'UN laissez-passer'


class Passport(Base):
    __tablename__ = "passports"
    id = Column(Integer, primary_key=True, index=True)
    passport_number = Column(String, unique=True, index=True)
    passport_type = Column(Enum(PassportType), nullable=False, index=True)
    issuer_country = Column(String, index=True)
    issue_date = Column(DateTime, default=datetime.now(tz=timezone.utc))
    expire_date = Column(DateTime, default=datetime.now(tz=timezone.utc))
    issue_place = Column(String, index=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, unique=True)

    user = Relationship('User', back_populates="passports")