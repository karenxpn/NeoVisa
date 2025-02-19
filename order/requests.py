from typing import Optional

from pydantic import BaseModel

from order.models import OrderStatus


class CreateOrderRequest(BaseModel):
    credential_id: int
    card_id: Optional[int] = None


class UpdateOrderRequest(BaseModel):
    status: OrderStatus
