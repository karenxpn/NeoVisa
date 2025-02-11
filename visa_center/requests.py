from pydantic import BaseModel, Field

from visa_center.models.visa_center_model import CountryEnum


class AddVisaAccountRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    country: CountryEnum = Field(...)
