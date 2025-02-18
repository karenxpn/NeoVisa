from typing import Optional

from pyasn1.type.univ import Boolean
from pydantic import BaseModel, Field, ConfigDict


class GatewayRequest(BaseModel):
    pass

class AttachCardRequest(BaseModel):
    order_id: str
    order_number: str


class CardResponse(BaseModel):
    class CardAuthInfo(BaseModel):
        pan: str = Field(..., alias="pan")
        cardholderName: str
        expiration: str

        model_config = ConfigDict(arbitrary_types_allowed=True)

    class BindingInfo(BaseModel):
        bindingId: str

        model_config = ConfigDict(arbitrary_types_allowed=True)

    class BankInfo(BaseModel):
        bankName: Optional[str] = None

        model_config = ConfigDict(arbitrary_types_allowed=True)

    bindingInfo: Optional[BindingInfo] = None
    cardAuthInfo: Optional[CardAuthInfo] = None
    bankInfo: Optional[BankInfo] = None
    error: Optional[bool] = None
    errorCode: Optional[int] = 0
    actionCode: Optional[int] = 0
    actionCodeDescription: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CardCreate(BaseModel):
    user_id: int
    binding_id: str
    card_number: str
    card_holder_name: str
    expiration_date: str
    bank_name: Optional[str] = None
    default_card: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


    @classmethod
    def from_response(cls, response: CardResponse, user_id: int) -> "CardCreate":
        expiration = response.cardAuthInfo.expiration
        return cls(
            user_id=user_id,
            binding_id=response.bindingInfo.bindingId,
            card_number=response.cardAuthInfo.pan,
            card_holder_name=response.cardAuthInfo.cardholderName,
            expiration_date=f"{expiration[:4]}/{expiration[4:]}",
            bank_name=response.bankInfo.bankName
        )