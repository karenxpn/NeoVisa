import re

from pydantic import BaseModel, field_validator

def validate_phone_number(value):
    phone_regex = re.compile(r'^\+?(\d{1,3})?[-.\s]?(\(?\d{3}\)?)[-.\s]?(\d{3})[-.\s]?(\d{4})$')
    if not phone_regex.match(value):
        raise ValueError('Invalid phone number')

    return value

class PhoneNumberRequest(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, value):
        return validate_phone_number(value)


class OTPRequest(BaseModel):
    phone_number: str
    otp: str

    @field_validator('phone_number')
    def validate_phone_number(cls, value):
        return validate_phone_number(value)


    @field_validator('otp')
    def validate_phone_number(cls, value):
        if len(value) != 6:
            raise ValueError('Invalid OTP')
        return value