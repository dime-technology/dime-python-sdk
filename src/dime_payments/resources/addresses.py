from __future__ import annotations

from typing import Any

from ..data_objects.address import Address
from ..data_objects.message_result import MessageResult
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Addresses(AbstractResource):
    def list(self, sid: str, uuid: str) -> CursorPage[Address]:
        body = self._envelope({'sid': sid, 'uuid': uuid})
        return self._paginate('GET', 'address/list', body, Address.from_dict)

    def show(self, sid: str, uuid: str, address_id: int | str) -> Address:
        raw = self._transport.request(
            'GET',
            'address/show',
            self._envelope({'sid': sid, 'uuid': uuid, 'address_id': address_id}),
        )
        return Address.from_dict(raw.get('data') or {})

    def create(self, sid: str, uuid: str, attributes: dict[str, Any]) -> Address:
        body = self._envelope({'sid': sid, 'uuid': uuid} | attributes)
        raw = self._transport.request('POST', 'address/create', body)
        return Address.from_dict(raw.get('data') or {})

    def update(self, sid: str, uuid: str, address_id: int | str, attributes: dict[str, Any]) -> Address:
        body = self._envelope({'sid': sid, 'uuid': uuid, 'address_id': address_id} | attributes)
        raw = self._transport.request('PATCH', 'address/update', body)
        return Address.from_dict(raw.get('data') or {})

    def delete(self, sid: str, uuid: str, address_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'uuid': uuid, 'address_id': address_id})
        raw = self._transport.request('POST', 'address/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)
