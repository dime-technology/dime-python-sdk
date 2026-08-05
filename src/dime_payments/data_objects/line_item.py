from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class LineItem:
    """
    A single line on an invoice. ``item_id`` points at the Merchant item the line
    was sourced from; ``name`` and ``unit_price`` are snapshotted at creation so
    later edits to the item do not rewrite history.
    """

    id: int | None = None
    item_id: int | None = None
    name: str | None = None
    description: str | None = None
    quantity: str | None = None
    unit_price: str | None = None
    amount: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LineItem':
        return cls(
            id=arr_int(data, 'id'),
            item_id=arr_int(data, 'item_id'),
            name=arr_string(data, 'name'),
            description=arr_string(data, 'description'),
            quantity=arr_string(data, 'quantity'),
            unit_price=arr_string(data, 'unit_price'),
            amount=arr_string(data, 'amount'),
        )
