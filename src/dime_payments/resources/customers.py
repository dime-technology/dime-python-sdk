from __future__ import annotations

from typing import Any

from ..data_objects.customer import Customer
from ..data_objects.message_result import MessageResult
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Customers(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Customer]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'customer/list', body, Customer.from_dict)

    def show(self, sid: str, filters: dict[str, Any]) -> Customer:
        raw = self._transport.request('GET', 'customer/show', self._envelope({'sid': sid}, filters))
        return Customer.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> Customer:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'customer/create', body)
        return Customer.from_dict(raw.get('data') or {})

    def update(self, sid: str, filters: dict[str, Any], attributes: dict[str, Any]) -> Customer:
        body = self._envelope({'sid': sid} | attributes, filters)
        raw = self._transport.request('PATCH', 'customer/update', body)
        return Customer.from_dict(raw.get('data') or {})

    def delete(self, sid: str, filters: dict[str, Any]) -> MessageResult:
        raw = self._transport.request('POST', 'customer/delete', self._envelope({'sid': sid}, filters))
        return MessageResult.from_dict(raw.get('data') or raw)
