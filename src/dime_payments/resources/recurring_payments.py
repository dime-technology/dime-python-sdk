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
        """
        Create a recurring payment schedule.

        ``attributes`` takes ``name``, ``amount``, ``start_date``,
        ``recurrence_schedule``, ``payment_method`` and ``customer_uuid``
        (required); ``end_date`` and ``shipping_address``;
        ``customer_covers_fee``, which when true treats ``amount`` as what the
        merchant nets and adds the processing fee on top of each charge; and
        ``item_id``, the item (designation) each run is credited to (omit it, or
        pass ``None``, for the merchant's default item).
        """
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'recurring-payment/create', body)
        return RecurringPayment.from_dict(raw.get('data') or {})

    def edit(self, sid: str, recurring_payment_id: int | str, attributes: dict[str, Any]) -> RecurringPayment:
        """
        Edit a recurring payment schedule. Omitted keys are left unchanged.

        ``attributes`` takes any of the :meth:`create` keys.
        ``customer_covers_fee`` true turns fee coverage on (grossing up
        ``amount``, or the current amount) and false turns it off. ``item_id``
        re-pins the item (designation); ``item_id=None`` unpins it, so each run
        is credited to whatever the merchant's default item is at the time.
        Unlike every other key, an explicit ``None`` ``item_id`` is sent rather
        than dropped.
        """
        body = self._envelope({'sid': sid, 'recurring_payment_id': recurring_payment_id} | attributes)
        if 'item_id' in attributes and attributes['item_id'] is None:
            body['data']['item_id'] = None
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
