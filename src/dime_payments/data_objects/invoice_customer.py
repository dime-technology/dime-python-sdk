from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class InvoiceCustomer:
    """The customer snapshot embedded in an invoice response."""

    id: int | None = None
    name: str | None = None
    email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoiceCustomer':
        return cls(
            id=arr_int(data, 'id'),
            name=arr_string(data, 'name'),
            email=arr_string(data, 'email'),
        )
