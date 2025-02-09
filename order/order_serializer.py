import datetime

from pydantic import BaseModel, ConfigDict

from order.models import OrderStatus
from visa_center.visa_center_credentials_serializer import VisaCenterCredentialsSerializer


class OrderSerializer(BaseModel):
    id: int
    status: OrderStatus
    user_id: int
    visa_credentials: VisaCenterCredentialsSerializer

    model_config = ConfigDict(from_attributes=True)
