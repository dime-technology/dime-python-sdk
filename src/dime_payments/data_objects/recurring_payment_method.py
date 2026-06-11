from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class RecurringPaymentMethod:
    id: int | None = None
    type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringPaymentMethod':
        return cls(
            id=arr_int(data, 'id'),
            type=arr_string(data, 'type'),
        )
