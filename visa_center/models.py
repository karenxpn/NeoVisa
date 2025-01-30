import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Relationship
from core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum



load_dotenv()

SECRET_KEY = os.environ.get('FERNET_SECRET_KEY')
cipher = Fernet(SECRET_KEY)

class CountryEnum(str, Enum):
    SPAIN = "ES"

class VisaCenterCredentials(Base):
    __tablename__ = 'visa_center_credentials'

    id = Column(Integer, primary_key=True, index=True)
    country = Column(SQLEnum(CountryEnum), nullable=False, default=CountryEnum.SPAIN)

    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    user = Relationship('User', back_populates='visa_credentials')


    def set_password(self, password: str):
        self.encrypted_password = cipher.encrypt(password.encode()).decode()

    def get_password(self) -> str:
        return cipher.decrypt(self.encrypted_password.encode()).decode()


