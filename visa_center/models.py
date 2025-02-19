import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy.types import DateTime


load_dotenv()

SECRET_KEY = os.environ.get('FERNET_SECRET_KEY')
cipher = Fernet(SECRET_KEY)

class CountryEnum(str, Enum):
    ES = "Spain"
    GR = "Greece"

class VisaCenterCredentials(Base):
    __tablename__ = 'visa_center_credentials'

    id = Column(Integer, primary_key=True, index=True)
    country = Column(SQLEnum(CountryEnum), nullable=False, default=CountryEnum.ES)

    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    user = relationship('User', back_populates='visa_credentials')

    orders = relationship("Order", back_populates="visa_credentials")
    passports = relationship("Passport", back_populates="credentials", cascade='all, delete-orphan')

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    def set_password(self, password: str):
        self.encrypted_password = cipher.encrypt(password.encode()).decode()

    def get_password(self) -> str:
        return cipher.decrypt(self.encrypted_password.encode()).decode()

    @property
    def passports_count(self):
        if hasattr(self, 'passports') and self.passports is not None:
            return len(self.passports)
        return 0



class PassportType(Enum):
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

    passport_number = Column(String, nullable=False, index=True)
    passport_type = Column(SQLEnum(PassportType), nullable=False, index=True, default=PassportType.FOREIGNERS)
    issuer_country = Column(String, nullable=False, index=True)
    issue_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)
    issue_place = Column(String, nullable=False, index=True)

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    nationality = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    user = relationship('User', back_populates='passports')

    credentials_id = Column(Integer, ForeignKey('visa_center_credentials.id', ondelete='CASCADE'), nullable=False, index=True)
    credentials = relationship('VisaCenterCredentials', back_populates='passports')

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))


