from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class InvoicePayment:
    """A payment recorded against an invoice."""

    amount: str | None = None
    paid_at: str | None = None
    method: str | None = None
    transaction_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoicePayment':
        return cls(
            amount=arr_string(data, 'amount'),
            paid_at=arr_string(data, 'paid_at'),
            method=arr_string(data, 'method'),
            transaction_id=arr_int(data, 'transaction_id'),
        )
