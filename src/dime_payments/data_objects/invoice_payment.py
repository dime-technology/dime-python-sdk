from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class InvoicePayment:
    """
    A payment recorded against an invoice.

    ``amount`` is what was credited to the invoice; ``cover_fee`` is the processing
    fee charged on top of it, so ``amount + cover_fee`` is what the customer
    actually paid. It is zero unless the invoice required the customer to cover
    fees.
    """

    amount: str | None = None
    cover_fee: str | None = None
    paid_at: str | None = None
    method: str | None = None
    transaction_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoicePayment':
        return cls(
            amount=arr_string(data, 'amount'),
            cover_fee=arr_string(data, 'cover_fee'),
            paid_at=arr_string(data, 'paid_at'),
            method=arr_string(data, 'method'),
            transaction_id=arr_int(data, 'transaction_id'),
        )
