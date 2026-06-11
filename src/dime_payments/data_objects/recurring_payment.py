from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_int, arr_object_from, arr_string
from .recurring_payment_method import RecurringPaymentMethod
from .transaction_address import TransactionAddress


@dataclass
class RecurringPayment:
    id: int | None = None
    name: str | None = None
    amount: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    recurrence_schedule: str | None = None
    last_run_date: str | None = None
    last_run_status: str | None = None
    last_run_failed_count: int | None = None
    next_run_date: str | None = None
    status: str | None = None
    paused_until_date: str | None = None
    customer_uuid: str | None = None
    cancelled_at: str | None = None
    error: str | None = None
    payment_method: RecurringPaymentMethod = field(default_factory=RecurringPaymentMethod)
    shipping_address: TransactionAddress = field(default_factory=TransactionAddress)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringPayment':
        return cls(
            id=arr_int(data, 'id'),
            name=arr_string(data, 'name'),
            amount=arr_string(data, 'amount'),
            start_date=arr_string(data, 'start_date'),
            end_date=arr_string(data, 'end_date'),
            recurrence_schedule=arr_string(data, 'recurrence_schedule'),
            last_run_date=arr_string(data, 'last_run_date'),
            last_run_status=arr_string(data, 'last_run_status'),
            last_run_failed_count=arr_int(data, 'last_run_failed_count'),
            next_run_date=arr_string(data, 'next_run_date'),
            status=arr_string(data, 'status'),
            paused_until_date=arr_string(data, 'paused_until_date'),
            customer_uuid=arr_string(data, 'customer_uuid'),
            cancelled_at=arr_string(data, 'cancelled_at'),
            error=arr_string(data, 'error'),
            payment_method=RecurringPaymentMethod.from_dict(
                arr_object_from(data, ['payment_method'])
            ),
            shipping_address=TransactionAddress.from_dict(
                arr_object_from(data, ['shipping_address'])
            ),
        )
