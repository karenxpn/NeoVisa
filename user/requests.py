from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None)

    # passport info
    passport_number: str = Field(None, min_length=6, max_length=20, pattern=r'^[A-Za-z0-9]+$')
    passport_type: str = Field(None, min_length=1)
    issuer_country: str = Field(None, min_length=1)
    issue_date: date
    expire_date: date
    issue_place: str = Field(None, min_length=1)

    # user info
    first_name: str = Field(None, min_length=1, pattern=r'^[a-zA-Z\s]+$')
    last_name: str = Field(None, min_length=1, pattern=r'^[a-zA-Z\s]+$')
    family_name: str = Field(None, min_length=1)
