from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_int, arr_object_from, arr_string
from .transaction import Transaction


@dataclass
class DepositWithTransactions:
    sid: str | None = None
    transaction_info_id: str | None = None
    transaction_id: str | None = None
    transaction_date: str | None = None
    fund_date: str | None = None
    type: str | None = None
    count_of_transactions: int | None = None
    trans_total: str | None = None
    transactions: list[Transaction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DepositWithTransactions':
        raw_txns = data.get('transactions', [])
        if isinstance(raw_txns, dict):
            raw_txns = list(raw_txns.values())
        transactions = [Transaction.from_dict(t) for t in raw_txns if isinstance(t, dict)]

        return cls(
            sid=arr_string(data, 'sid'),
            transaction_info_id=arr_string(data, 'transaction_info_id'),
            transaction_id=arr_string(data, 'transaction_id'),
            transaction_date=arr_string(data, 'transaction_date'),
            fund_date=arr_string(data, 'fund_date'),
            type=arr_string(data, 'type'),
            count_of_transactions=arr_int(data, 'countOfTransactions'),
            trans_total=arr_string(data, 'transTotal'),
            transactions=transactions,
        )
