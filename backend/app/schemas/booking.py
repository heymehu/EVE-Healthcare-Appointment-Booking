from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, computed_field, field_serializer, field_validator

from app.schemas.centre import CentreOut
from app.schemas.test import TestOut


class BookingCreate(BaseModel):
    test_id: int
    centre_id: int
    appointment_date: date
    appointment_time: time

    @field_validator("appointment_date")
    @classmethod
    def date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return value


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    test_id: int
    centre_id: int
    appointment_date: date
    appointment_time: time
    amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    test: TestOut | None = None
    centre: CentreOut | None = None

    @computed_field
    @property
    def booking_code(self) -> str:
        return f"BK{self.id:04d}"

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> float:
        return float(value)


class BookingListResponse(BaseModel):
    items: list[BookingOut]
    total: int
