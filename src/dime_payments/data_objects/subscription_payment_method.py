from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class SubscriptionPaymentMethod:
    id: int | None = None
    type: str | None = None
    last_four: str | None = None
    expiration: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SubscriptionPaymentMethod':
        return cls(
            id=arr_int(data, 'id'),
            type=arr_string(data, 'type'),
            last_four=arr_string(data, 'last_four'),
            expiration=arr_string(data, 'expiration'),
        )
