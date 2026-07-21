from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class RecurringInvoice:
    id: int | None = None
    sid: str | None = None
    customer_uuid: str | None = None
    frequency: str | None = None
    amount: str | None = None
    status: str | None = None
    start_date: str | None = None
    next_invoice_date: str | None = None
    last_invoice_date: str | None = None
    cancelled_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringInvoice':
        return cls(
            id=arr_int(data, 'id'),
            sid=arr_string(data, 'sid'),
            customer_uuid=arr_string(data, 'customer_uuid'),
            frequency=arr_string(data, 'frequency'),
            amount=arr_string(data, 'amount'),
            status=arr_string(data, 'status'),
            start_date=arr_string(data, 'start_date'),
            next_invoice_date=arr_string(data, 'next_invoice_date'),
            last_invoice_date=arr_string(data, 'last_invoice_date'),
            cancelled_at=arr_string(data, 'cancelled_at'),
            created_at=arr_string(data, 'created_at'),
            updated_at=arr_string(data, 'updated_at'),
        )
