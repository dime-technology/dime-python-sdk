from __future__ import annotations

from typing import Any

from ..data_objects.subscription import Subscription
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Subscriptions(AbstractResource):
    """
    Endpoints for customers' subscriptions to a plan. Requires the matching
    ``subscription:*`` ability. Start a subscription with
    :meth:`SubscriptionPlans.subscribe`.
    """

    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Subscription]:
        """
        List subscriptions, newest first.

        ``filters`` takes ``status`` (``Active``, ``Failed``, ``Paused``,
        ``Cancelled`` or ``Ended``) and ``customer_uuid``. A merchant with no
        subscriptions returns an empty page, not an error.
        """
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'subscription/list', body, Subscription.from_dict)

    def show(self, sid: str, subscription_id: int | str) -> Subscription:
        body = self._envelope({'sid': sid, 'subscription_id': subscription_id})
        raw = self._transport.request('GET', 'subscription/show', body)
        return Subscription.from_dict(raw.get('data') or {})

    def pause(self, sid: str, subscription_id: int | str, pause_until_date: str | None = None) -> Subscription:
        """Pause until ``pause_until_date`` (a future date), or indefinitely if omitted."""
        body = self._envelope({
            'sid': sid,
            'subscription_id': subscription_id,
            'pause_until_date': pause_until_date,
        })
        raw = self._transport.request('PATCH', 'subscription/pause', body)
        return Subscription.from_dict(raw.get('data') or {})

    def resume(self, sid: str, subscription_id: int | str) -> Subscription:
        """Reactivate a paused subscription and recompute its next charge date."""
        body = self._envelope({'sid': sid, 'subscription_id': subscription_id})
        raw = self._transport.request('PATCH', 'subscription/resume', body)
        return Subscription.from_dict(raw.get('data') or {})

    def cancel(self, sid: str, subscription_id: int | str) -> Subscription:
        """Cancel permanently. No further charges are made."""
        body = self._envelope({'sid': sid, 'subscription_id': subscription_id})
        raw = self._transport.request('PATCH', 'subscription/cancel', body)
        return Subscription.from_dict(raw.get('data') or {})
