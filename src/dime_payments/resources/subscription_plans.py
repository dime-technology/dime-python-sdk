from __future__ import annotations

from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.subscribe_result import SubscribeResult
from ..data_objects.subscription_plan import SubscriptionPlan
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class SubscriptionPlans(AbstractResource):
    def list(self, sid: str, status: str | None = None) -> CursorPage[SubscriptionPlan]:
        body = self._envelope({'sid': sid, 'status': status})
        return self._paginate('GET', 'subscription-plan/list', body, SubscriptionPlan.from_dict)

    def show(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('GET', 'subscription-plan/show', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> SubscriptionPlan:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'subscription-plan/create', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def update(
        self,
        sid: str,
        subscription_plan_id: int | str,
        attributes: dict[str, Any],
    ) -> SubscriptionPlan:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id} | attributes)
        raw = self._transport.request('PATCH', 'subscription-plan/edit', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def delete(self, sid: str, subscription_plan_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('POST', 'subscription-plan/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def publish(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('PATCH', 'subscription-plan/publish', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def archive(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
        body = self._envelope({'sid': sid, 'subscription_plan_id': subscription_plan_id})
        raw = self._transport.request('PATCH', 'subscription-plan/archive', body)
        return SubscriptionPlan.from_dict(raw.get('data') or {})

    def unarchive(self, sid: str, subscription_plan_id: int | str) -> SubscriptionPlan:
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
        body = self._envelope({
            'sid': sid,
            'subscription_plan_id': subscription_plan_id,
            'customer_uuid': customer_uuid,
            'payment_method': payment_method,
        })
        raw = self._transport.request('POST', 'subscription-plan/subscribe', body)
        return SubscribeResult.from_dict(raw.get('data') or {})
