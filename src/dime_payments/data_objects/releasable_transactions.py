from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_bool, arr_string


@dataclass
class ReleasableTransaction:
    """
    A held-funds payment that can be released now. ``amount`` is what releasing
    it would pay the merchant: ``net_amount`` less ``split_amount``. ``type`` is
    ``CC`` or ``ACH``.
    """

    transaction_info_id: str | None = None
    type: str | None = None
    transaction_date: str | None = None
    gross_amount: str | None = None
    net_amount: str | None = None
    split_amount: str | None = None
    amount: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ReleasableTransaction':
        return cls(
            transaction_info_id=arr_string(data, 'transaction_info_id'),
            type=arr_string(data, 'type'),
            transaction_date=arr_string(data, 'transaction_date'),
            gross_amount=arr_string(data, 'gross_amount'),
            net_amount=arr_string(data, 'net_amount'),
            split_amount=arr_string(data, 'split_amount'),
            amount=arr_string(data, 'amount'),
        )


@dataclass
class ReleasableTransactions:
    """
    The payments a held-funds merchant can release, newest first, up to 500.
    ``truncated`` is true when there are more than were listed.
    """

    sid: str | None = None
    transactions: list[ReleasableTransaction] = field(default_factory=list)
    total: str | None = None
    truncated: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ReleasableTransactions':
        return cls(
            sid=arr_string(data, 'sid'),
            transactions=[
                ReleasableTransaction.from_dict(t) for t in arr_array(data, 'transactions') if isinstance(t, dict)
            ],
            total=arr_string(data, 'total'),
            truncated=arr_bool(data, 'truncated'),
        )
