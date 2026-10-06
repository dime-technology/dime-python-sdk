from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class SubscriptionPaymentMethod:
    """
    The saved payment method a subscription charges. ``type`` is ``cc`` or
    ``ach``; ``last_four`` and ``expiration`` are set for a card, ``bank_name``
    and ``account_type`` for a bank account.
    """

    id: int | None = None
    type: str | None = None
    last_four: str | None = None
    expiration: str | None = None
    bank_name: str | None = None
    account_type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SubscriptionPaymentMethod':
        return cls(
            id=arr_int(data, 'id'),
            type=arr_string(data, 'type'),
            last_four=arr_string(data, 'last_four'),
            expiration=arr_string(data, 'expiration'),
            bank_name=arr_string(data, 'bank_name'),
            account_type=arr_string(data, 'account_type'),
        )
