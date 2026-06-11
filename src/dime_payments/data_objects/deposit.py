from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class Deposit:
    transaction_date: str | None = None
    fund_date: str | None = None
    transaction_info_id: str | None = None
    transaction_id: str | None = None
    transaction_detail_account: str | None = None
    authorization_amount: str | None = None
    net_amount: str | None = None
    sweep_id: str | None = None
    type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Deposit':
        return cls(
            transaction_date=arr_string(data, 'transaction_date'),
            fund_date=arr_string(data, 'fund_date'),
            transaction_info_id=arr_string(data, 'transaction_info_id'),
            transaction_id=arr_string(data, 'transaction_id'),
            transaction_detail_account=arr_string(data, 'transaction_detail_account'),
            authorization_amount=arr_string(data, 'authorization_amount'),
            net_amount=arr_string(data, 'net_amount'),
            sweep_id=arr_string(data, 'sweep_id'),
            type=arr_string(data, 'type'),
        )
