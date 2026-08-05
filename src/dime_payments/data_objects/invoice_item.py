from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_int, arr_string


@dataclass
class InvoiceItem:
    """
    A Merchant item (fund or designation) that invoice line items reference by
    ``item_id``. This is the catalog entry, not a line on an invoice — for that,
    see :class:`LineItem`.
    """

    id: int | None = None
    name: str | None = None
    description: str | None = None
    price: str | None = None
    tax_deductible: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoiceItem':
        return cls(
            id=arr_int(data, 'id'),
            name=arr_string(data, 'name'),
            description=arr_string(data, 'description'),
            price=arr_string(data, 'price'),
            tax_deductible=arr_bool(data, 'tax_deductible'),
        )
