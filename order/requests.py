from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    credential_id: int