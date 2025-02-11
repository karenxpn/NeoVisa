from sqlalchemy import Column, String, Integer, DateTime
from core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum


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
    passport_number = Column(String, unique=True, nullable=False, index=True)
    passport_type = Column(SQLEnum(PassportType), nullable=False, index=True, default=PassportType.FOREIGNERS)
    issuer_country = Column(String, nullable=False, index=True)
    issue_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)
    issue_place = Column(String, nullable=False, index=True)

