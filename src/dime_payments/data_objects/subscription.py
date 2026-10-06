from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_int, arr_object, arr_string
from .subscription_item import SubscriptionItem
from .subscription_payment_method import SubscriptionPaymentMethod


@dataclass
class Subscription:
    """
    A customer's enrollment in a :class:`SubscriptionPlan`.

    ``status`` is one of ``Active``, ``Failed``, ``Paused``, ``Cancelled`` or
    ``Ended``. ``items`` is populated by :meth:`Subscriptions.show` only; list
    and lifecycle responses leave it empty.
    """

    id: int | None = None
    subscription_plan_id: int | None = None
    plan_name: str | None = None
    amount: str | None = None
    recurrence_schedule: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    last_run_date: str | None = None
    last_run_status: str | None = None
    last_run_failed_count: int | None = None
    next_run_date: str | None = None
    status: str | None = None
    paused_until_date: str | None = None
    cancelled_at: str | None = None
    cancelled_by: str | None = None
    customer_uuid: str | None = None
    error: str | None = None
    payment_method: SubscriptionPaymentMethod = field(default_factory=SubscriptionPaymentMethod)
    items: list[SubscriptionItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Subscription':
        return cls(
            id=arr_int(data, 'id'),
            subscription_plan_id=arr_int(data, 'subscription_plan_id'),
            plan_name=arr_string(data, 'plan_name'),
            amount=arr_string(data, 'amount'),
            recurrence_schedule=arr_string(data, 'recurrence_schedule'),
            start_date=arr_string(data, 'start_date'),
            end_date=arr_string(data, 'end_date'),
            last_run_date=arr_string(data, 'last_run_date'),
            last_run_status=arr_string(data, 'last_run_status'),
            last_run_failed_count=arr_int(data, 'last_run_failed_count'),
            next_run_date=arr_string(data, 'next_run_date'),
            status=arr_string(data, 'status'),
            paused_until_date=arr_string(data, 'paused_until_date'),
            cancelled_at=arr_string(data, 'cancelled_at'),
            cancelled_by=arr_string(data, 'cancelled_by'),
            customer_uuid=arr_string(data, 'customer_uuid'),
            error=arr_string(data, 'error'),
            payment_method=SubscriptionPaymentMethod.from_dict(arr_object(data, 'payment_method')),
            items=[SubscriptionItem.from_dict(i) for i in arr_array(data, 'items') if isinstance(i, dict)],
        )
