from pydantic import BaseModel, ConfigDict

from visa_center.models import CountryEnum


class VisaCenterCredentialsSerializer(BaseModel):
    id: int
    country: CountryEnum
    username: str
    encrypted_password: str

    model_config = ConfigDict(from_attributes=True)
