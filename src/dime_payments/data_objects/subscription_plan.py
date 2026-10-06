from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_bool, arr_int, arr_string
from .subscription_item import SubscriptionItem


@dataclass
class SubscriptionPlan:
    """
    A recurring offering customers subscribe to.

    ``status`` is ``draft``, ``active`` or ``archived``; only an active plan
    accepts new subscribers. ``recurrence_schedule`` is one of ``Weekly``,
    ``Biweekly``, ``FirstFifteenth``, ``Monthly`` or ``Yearly``.
    """

    id: int | None = None
    name: str | None = None
    description: str | None = None
    recurrence_schedule: str | None = None
    status: str | None = None
    subtotal: str | None = None
    total: str | None = None
    token: str | None = None
    public_url: str | None = None
    allow_public: bool = False
    created_at: str | None = None
    items: list[SubscriptionItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SubscriptionPlan':
        return cls(
            id=arr_int(data, 'id'),
            name=arr_string(data, 'name'),
            description=arr_string(data, 'description'),
            recurrence_schedule=arr_string(data, 'recurrence_schedule'),
            status=arr_string(data, 'status'),
            subtotal=arr_string(data, 'subtotal'),
            total=arr_string(data, 'total'),
            token=arr_string(data, 'token'),
            public_url=arr_string(data, 'public_url'),
            allow_public=arr_bool(data, 'allow_public'),
            created_at=arr_string(data, 'created_at'),
            items=[SubscriptionItem.from_dict(i) for i in arr_array(data, 'items') if isinstance(i, dict)],
        )
