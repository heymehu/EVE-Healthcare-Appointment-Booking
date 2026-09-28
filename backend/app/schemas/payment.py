from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.booking import BookingOut


class PaymentCreate(BaseModel):
    booking_id: int
    simulate_status: Literal["SUCCESS", "FAILED", "AUTO"] = "AUTO"


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    status: str
    provider_event_id: str
    created_at: datetime
    updated_at: datetime
    booking: BookingOut | None = None


class WebhookPayload(BaseModel):
    event_id: str = Field(min_length=3, max_length=100)
    payment_id: int
    booking_id: int
    status: Literal["SUCCESS", "FAILED"]


class WebhookResponse(BaseModel):
    processed: bool
    idempotent: bool = False
    message: str
    payment: PaymentOut | None = None
