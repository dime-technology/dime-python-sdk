from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class LineItem:
    id: int | None = None
    invoice_id: int | None = None
    item_id: str | None = None
    description: str | None = None
    quantity: str | None = None
    amount: str | None = None
    total: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LineItem':
        return cls(
            id=arr_int(data, 'id'),
            invoice_id=arr_int(data, 'invoice_id'),
            item_id=arr_string(data, 'item_id'),
            description=arr_string(data, 'description'),
            quantity=arr_string(data, 'quantity'),
            amount=arr_string(data, 'amount'),
            total=arr_string(data, 'total'),
        )