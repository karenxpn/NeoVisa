from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.v1 import constr


class UpdateUserRequest(BaseModel):
    email: EmailStr

    # passport info
    passport_number: constr(min_length=6, max_length=20, regex=r'^[A-Za-z0-9]+$')
    passport_type: constr(min_length=1)
    issuer_country: constr(min_length=1)
    issue_date: date
    expire_date: date
    issue_place: constr(min_length=1)

    # user info
    first_name: constr(min_length=1, regex=r'^[a-zA-Z\s]+$')
    last_name: Optional[constr(min_length=1, regex=r'^[a-zA-Z\s]+$')] = None
    family_name: constr(min_length=1)
