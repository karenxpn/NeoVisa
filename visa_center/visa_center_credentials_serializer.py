from pydantic import BaseModel, ConfigDict

from visa_center.models.visa_center_model import CountryEnum


class VisaCenterCredentialsSerializer(BaseModel):
    id: int
    country: CountryEnum
    username: str
    encrypted_password: str

    model_config = ConfigDict(from_attributes=True)
