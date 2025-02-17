from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    phone_number = Column(String, index=True, unique=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    family_name = Column(String, index=True)

    email = Relationship('Email', back_populates='user', uselist=False, passive_deletes=True)
    visa_credentials = Relationship('VisaCenterCredentials', back_populates='user', passive_deletes=True)
    orders = Relationship('Order', back_populates='user', passive_deletes=True)
    passports = Relationship('Passport', back_populates='user', cascade='all, delete-orphan')
    cards = Relationship('Card', back_populates='user',  cascade='all, delete-orphan')


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, unique=True)
    user = Relationship('User', back_populates='email')