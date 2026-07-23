from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class SubscribeResult:
    subscription_id: int | None = None
    status: str | None = None
    next_run_date: str | None = None
    transaction_number: str | None = None
    amount: str | None = None
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SubscribeResult':
        return cls(
            subscription_id=arr_int(data, 'subscription_id'),
            status=arr_string(data, 'status'),
            next_run_date=arr_string(data, 'next_run_date'),
            transaction_number=arr_string(data, 'transaction_number'),
            amount=arr_string(data, 'amount'),
            message=arr_string(data, 'message'),
        )
