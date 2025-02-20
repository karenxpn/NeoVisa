from typing import List

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from visa_center.models import CountryEnum


class VisaCenterCredentialsSerializer(BaseModel):
    id: int
    country: CountryEnum
    username: str
    encrypted_password: str
    passports_count: int

    model_config = ConfigDict(from_attributes=True)