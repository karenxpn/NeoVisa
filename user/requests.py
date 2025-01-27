from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None)
    first_name: str = Field(None, min_length=1, pattern=r'^[a-zA-Z\s]+$')
    last_name: str = Field(None, min_length=1, pattern=r'^[a-zA-Z\s]+$')
    family_name: str = Field(None, min_length=1)

update_user_whitelist = {
    'first_name',
    'last_name',
    'family_name',
}
