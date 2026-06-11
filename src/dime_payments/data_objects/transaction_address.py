from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class TransactionAddress:
    first_name: str | None = None
    last_name: str | None = None
    addr1: str | None = None
    addr2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TransactionAddress':
        return cls(
            first_name=arr_string(data, 'first_name'),
            last_name=arr_string(data, 'last_name'),
            addr1=arr_string(data, 'addr1'),
            addr2=arr_string(data, 'addr2'),
            city=arr_string(data, 'city'),
            state=arr_string(data, 'state'),
            zip=arr_string(data, 'zip'),
        )
