from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_int, arr_string
from .deposit_with_transactions import DepositWithTransactions


@dataclass
class DepositGroup:
    sid: str | None = None
    count: int | None = None
    deposits: list[DepositWithTransactions] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DepositGroup':
        raw_deposits = data.get('deposits', {})
        if isinstance(raw_deposits, dict):
            raw_deposits = list(raw_deposits.values())
        deposits = [DepositWithTransactions.from_dict(d) for d in raw_deposits if isinstance(d, dict)]

        return cls(
            sid=arr_string(data, 'sid'),
            count=arr_int(data, 'count'),
            deposits=deposits,
        )
