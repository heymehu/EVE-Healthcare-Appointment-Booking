from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class TestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    centre_id: int
    name: str
    description: str | None = None
    category: str
    price: Decimal
    created_at: datetime

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> float:
        return float(value)
