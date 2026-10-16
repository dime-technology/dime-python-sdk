from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class RecurringPaymentItem:
    """
    The item (designation) a :class:`RecurringPayment` is pinned to, which each
    run is credited to. ``name`` can be ``None`` while ``id`` is set, when the
    API does not disclose the item's name.
    """

    id: int | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringPaymentItem':
        return cls(id=arr_int(data, 'id'), name=arr_string(data, 'name'))
