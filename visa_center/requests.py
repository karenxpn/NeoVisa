from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic.v1.fields import Undefined

from visa_center.models import CountryEnum, PassportType


class VisaAccountPassport(BaseModel):
    passport_number: str = Field(min_length=6, max_length=20, pattern=r'^[A-Za-z0-9]+$')
    passport_type: PassportType = Field(...)
    issuer_country: str = Field(min_length=1)
    issue_date: date
    expire_date: date
    issue_place: Optional[str] = Field(None, min_length=1)

    name: str = Field(min_length=1)
    surname: str = Field(min_length=1)
    nationality: str = Field(min_length=1)


class AddVisaAccountCredentialsRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    country: CountryEnum = Field(...)

    passports: Optional[List[VisaAccountPassport]] = None


class VisaAccountCredentialsResponse(BaseModel):
    id: int
    country: str
    username: str
    user_id: int
    passports: Optional[List[VisaAccountPassport]] = Field(default=Undefined)

    class Config:
        from_attributes = True


class UpdateVisaAccountRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    country: Optional[CountryEnum] = None

    class Config:
        from_attributes = True


class UpdatePassportRequest(BaseModel):
    passport_type: Optional[PassportType] = None
    issuer_country: Optional[str] = Field(None, min_length=1)
    issue_date: Optional[date] = None
    expire_date: Optional[date] = None
    issue_place: Optional[str] = Field(None, min_length=1)

    name: Optional[str] = Field(None, min_length=1)
    surname: Optional[str] = Field(None, min_length=1)
    nationality: Optional[str] = Field(None, min_length=1)


class AddVisaCenterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    address: Optional[str] = Field(None, min_length=1)


class UpdateVisaCenterRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    address: Optional[str] = Field(None, min_length=1)

class VisaCenterResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None