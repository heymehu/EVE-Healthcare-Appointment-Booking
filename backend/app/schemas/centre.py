from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class CentreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    description: str | None = None
    image_url: str | None = None
    rating: Decimal | None = None
    review_count: int = 0
    available_tests: int = 0
    centre_type: str = "Diagnostic Center"
    address: str | None = None
    city: str | None = None
    pincode: str | None = None
    phone: str | None = None
    accreditation: str | None = None
    panels: str | None = None
    open_time: str | None = None
    is_open_now: bool = True
    starting_price: Decimal | None = None
    created_at: datetime

    @field_serializer("rating", "starting_price")
    def serialize_money(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class CentreListResponse(BaseModel):
    items: list[CentreOut]
    total: int
    page: int
    page_size: int


class CategoryOut(BaseModel):
    id: str
    name: str
    centre_count: int
    test_count: int
    min_price: float | None = None
    max_price: float | None = None


class CategoryListResponse(BaseModel):
    items: list[CategoryOut]
