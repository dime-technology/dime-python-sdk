from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class SubscriptionItem:
    name: str | None = None
    description: str | None = None
    quantity: str | None = None
    unit_price: str | None = None
    amount: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SubscriptionItem':
        return cls(
            name=arr_string(data, 'name'),
            description=arr_string(data, 'description'),
            quantity=arr_string(data, 'quantity'),
            unit_price=arr_string(data, 'unit_price'),
            amount=arr_string(data, 'amount'),
        )
