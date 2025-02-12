from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
from visa_center.models import CountryEnum


class AddVisaAccountPassport(BaseModel):
    passport_number: str = Field(min_length=6, max_length=20, pattern=r'^[A-Za-z0-9]+$')
    passport_type: str = Field(min_length=1)
    issuer_country: str = Field(min_length=1)
    issue_date: date
    expire_date: date
    issue_place: Optional[str] = Field(None, min_length=1)

    name: str = Field(min_length=1)
    surname: str = Field(min_length=1)
    nationality: str = Field(min_length=1)


class AddVisaAccountRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    country: CountryEnum = Field(...)

    passports: Optional[List[AddVisaAccountPassport]] = None
