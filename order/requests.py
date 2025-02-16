from pydantic import BaseModel

from order.models import OrderStatus


class CreateOrderRequest(BaseModel):
    credential_id: int


class UpdateOrderRequest(BaseModel):
    status: OrderStatus
