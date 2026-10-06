from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_int, arr_string


@dataclass
class HeldBalance:
    """
    A held-funds merchant's balance at the processor, in dollars.

    ``releasable`` is the figure that matters and the one a release is checked
    against: ``available`` less ``at_risk`` (ACH still inside the return window),
    ``owed_to_split`` (takings promised to another account), ``unresolved``
    (releases requested and not yet confirmed) and ``release_fee``, never below
    zero and never above ``ach_out_limit_remaining``.

    Money is kept as strings, consistent with the rest of the SDK, to avoid float
    rounding.
    """

    sid: str | None = None
    available: str | None = None
    pending: str | None = None
    reserve: str | None = None
    at_risk: str | None = None
    owed_to_split: str | None = None
    unresolved: str | None = None
    release_fee: str | None = None
    releasable: str | None = None
    ach_settlement_days: int | None = None
    ach_out_enabled: bool = False
    ach_out_limit_remaining: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'HeldBalance':
        return cls(
            sid=arr_string(data, 'sid'),
            available=arr_string(data, 'available'),
            pending=arr_string(data, 'pending'),
            reserve=arr_string(data, 'reserve'),
            at_risk=arr_string(data, 'at_risk'),
            owed_to_split=arr_string(data, 'owed_to_split'),
            unresolved=arr_string(data, 'unresolved'),
            release_fee=arr_string(data, 'release_fee'),
            releasable=arr_string(data, 'releasable'),
            ach_settlement_days=arr_int(data, 'ach_settlement_days'),
            ach_out_enabled=arr_bool(data, 'ach_out_enabled'),
            ach_out_limit_remaining=arr_string(data, 'ach_out_limit_remaining'),
        )
