from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    phone_number = Column(String, index=True, unique=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    family_name = Column(String, index=True)

    email = relationship('Email', back_populates='user', uselist=False, passive_deletes=True)
    visa_credentials = relationship('VisaCenterCredentials', back_populates='user', passive_deletes=True)
    orders = relationship('Order', back_populates='user', passive_deletes=True)
    passports = relationship('Passport', back_populates='user', cascade='all, delete-orphan')
    cards = relationship('Card', back_populates='user',  cascade='all, delete-orphan')


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, unique=True)
    user = relationship('User', back_populates='email')