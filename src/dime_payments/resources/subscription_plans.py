from __future__ import annotations

from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.subscribe_result import SubscribeResult
from ..data_objects.subscription_plan import SubscriptionPlan
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class SubscriptionPlans(AbstractResource):
    """
    Subscription plan endpoints. Requires the matching ``subscription-plan:*``
    ability.

    A plan is created as a draft, published to accept subscribers, and archived
    to stop taking new ones. Existing subscribers keep their own snapshot of the
    plan, so editing or archiving it does not change what they are charged.
    """

    def list(self, sid: str, status: str | None = None) -> CursorPage[SubscriptionPlan]:
        """List plans, newest first. ``status`` is ``draft``, ``active`` or ``archived``."""
        body = self._envelope({'sid': sid, 'status': status})
        return self._paginate('GET', 'subscription-plan/list', body, SubscriptionPlan.from_dict)

    def show(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('GET', 'subscription-plan/show', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> SubscriptionPlan:
        """
        Create a draft plan. Requires ``name``, ``recurrence_schedule``
        (``Weekly`` | ``Biweekly`` | ``FirstFifteenth`` | ``Monthly`` |
        ``Yearly``) and at least one entry in ``lines``, each with a Merchant
        ``item_id``, ``name``, ``quantity`` and ``unit_price``. ``description``
        and ``allow_public`` are optional.
        """
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'subscription-plan/create', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def edit(self, sid: str, subscription_plan_id: int | str, attributes: dict[str, Any]) -> SubscriptionPlan:
        """
        Replace the plan's fields and lines wholesale: send the full plan, as for
        :meth:`create`, not just the fields that changed.
        """
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id} | attributes)
        raw = self._transport.request('PATCH', 'subscription-plan/edit', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def delete(self, sid: str, subscription_plan_id: int | str) -> MessageResult:
        """Delete a plan with no subscribers. Archive one that has them."""
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('POST', 'subscription-plan/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def publish(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        """Move a draft plan with at least one line to active."""
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('PATCH', 'subscription-plan/publish', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def archive(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        """Stop new subscriptions and hide the plan from the public catalog."""
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('PATCH', 'subscription-plan/archive', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def unarchive(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        """Move an archived plan back to draft, to be reviewed and re-published."""
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('PATCH', 'subscription-plan/unarchive', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def subscribe(
        self,
        sid: str,
        subscription_plan_id: int | str,
        customer_uuid: str,
        payment_method: int | str,
    ) -> SubscribeResult:
        """
        Enroll a customer in an active plan, charging the first payment now to
        ``payment_method`` (one of the customer's saved payment method ids). A
        declined charge raises :class:`ValidationException` (422) and creates no
        subscription.
        """
        body = self._envelope({
            'sid': sid,
            'subscription_plan_id': subscription_plan_id,
            'customer_uuid': customer_uuid,
            'payment_method': payment_method,
        })
        raw = self._transport.request('POST', 'subscription-plan/subscribe', body)
        return SubscribeResult.from_dict(raw.get('data') or {})
