from pydantic import BaseModel, Field


class GatewayRequest(BaseModel):
    pass

class AttachCardRequest(BaseModel):
    order_id: str
    order_number: str
