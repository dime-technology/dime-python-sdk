from __future__ import annotations

from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.payment_method import PaymentMethod
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class PaymentMethods(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any]) -> CursorPage[PaymentMethod]:
        body = self._envelope({'sid': sid}, filters)
        return self._paginate('GET', 'payment-method/list', body, PaymentMethod.from_dict)

    def show(self, sid: str, payment_method_id: int | str, filters: dict[str, Any]) -> PaymentMethod:
        raw = self._transport.request(
            'GET',
            'payment-method/show',
            self._envelope({'sid': sid, 'payment_method_id': payment_method_id}, filters),
        )
        return PaymentMethod.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> PaymentMethod:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'payment-method/create', body)
        return PaymentMethod.from_dict(raw.get('data') or {})

    def update(self, sid: str, attributes: dict[str, Any]) -> PaymentMethod:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('PATCH', 'payment-method/update', body)
        return PaymentMethod.from_dict(raw.get('data') or {})

    def delete(self, sid: str, payment_method_id: int | str, uuid: str) -> MessageResult:
        body = self._envelope({'sid': sid, 'payment_method_id': payment_method_id, 'uuid': uuid})
        raw = self._transport.request('POST', 'payment-method/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)
