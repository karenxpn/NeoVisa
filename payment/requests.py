from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment.models import Card


class GatewayRequest(BaseModel):
    amount: int = Field(..., gt=0)

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
    orderStatus: Optional[int] = -1

    def is_error(self) -> bool:
        return bool(self.error) or self.errorCode != 0 or self.actionCode != 0


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
    async def from_response(cls, response: CardResponse, user_id: int, binding_id: str, db: AsyncSession) -> "CardCreate":
        if response.is_error() or not all([response.bindingInfo, response.cardAuthInfo, response.bankInfo]):
            raise ValueError("Cannot create card from error response or missing data")

        # Check if user has any cards
        result = await db.execute(
            select(Card).where(Card.user_id == user_id)
        )

        cards = result.scalars().all()


        has_cards = bool(cards)

        if any(c.binding_id == binding_id for c in cards):
            raise HTTPException(status_code=500, detail=f"Given card is already in use.")

        expiration = response.cardAuthInfo.expiration
        return cls(
            user_id=user_id,
            binding_id=response.bindingInfo.bindingId,
            card_number=response.cardAuthInfo.pan,
            card_holder_name=response.cardAuthInfo.cardholderName,
            expiration_date=f"{expiration[:4]}/{expiration[4:]}",
            bank_name=response.bankInfo.bankName,
            default_card=not has_cards
        )