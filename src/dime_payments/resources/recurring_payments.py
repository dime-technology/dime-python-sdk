from __future__ import annotations

from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.recurring_payment import RecurringPayment
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class RecurringPayments(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[RecurringPayment]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'recurring-payment/list', body, RecurringPayment.from_dict)

    def show(self, sid: str, recurring_payment_id: int | str) -> RecurringPayment:
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id})
        raw = self._transport.request('GET', 'recurring-payment/show', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> RecurringPayment:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'recurring-payment/create', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def edit(self, sid: str, recurring_payment_id: int | str, attributes: dict[str, Any]) -> RecurringPayment:
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id} | attributes)
        raw = self._transport.request('PATCH', 'recurring-payment/edit', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def pause(self, sid: str, recurring_payment_id: int | str, pause_until_date: str | None = None) -> RecurringPayment:
        body = self._envelope({
            'sid': sid,
            'recurring_payment_id': recurring_payment_id,
            'pause_until_date': pause_until_date,
        })
        raw = self._transport.request('PATCH', 'recurring-payment/pause', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def cancel(self, sid: str, recurring_payment_id: int | str) -> RecurringPayment:
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id})
        raw = self._transport.request('PATCH', 'recurring-payment/cancel', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def activate(self, sid: str, recurring_payment_id: int | str) -> RecurringPayment:
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id})
        raw = self._transport.request('PATCH', 'recurring-payment/activate', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def delete(self, sid: str, recurring_payment_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id})
        raw = self._transport.request('POST', 'recurring-payment/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)
