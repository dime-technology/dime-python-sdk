from __future__ import annotations

from typing import Any

from ..data_objects.form_link import FormLink
from ..data_objects.invoice import Invoice
from ..data_objects.line_item import LineItem
from ..data_objects.message_result import MessageResult
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Invoices(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Invoice]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'invoices', body, Invoice.from_dict)

    def show(self, sid: str, invoice_id: int | str) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('GET', 'invoice', body)
        return Invoice.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> Invoice:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'invoice/create', body)
        return Invoice.from_dict(raw.get('data') or {})

    def update(self, sid: str, invoice_id: int | str, attributes: dict[str, Any]) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id} | attributes)
        raw = self._transport.request('PATCH', 'invoice/update', body)
        return Invoice.from_dict(raw.get('data') or {})

    def delete(self, sid: str, invoice_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def send(self, sid: str, invoice_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/send', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def mark_sent(self, sid: str, invoice_id: int | str) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/mark-sent', body)
        return Invoice.from_dict(raw.get('data') or {})

    def void(self, sid: str, invoice_id: int | str) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('PATCH', 'invoice/void', body)
        return Invoice.from_dict(raw.get('data') or {})

    def duplicate(self, sid: str, invoice_id: int | str) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/duplicate', body)
        return Invoice.from_dict(raw.get('data') or {})

    def pay(self, sid: str, invoice_id: int | str, amount: str | None = None) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id, 'amount': amount})
        raw = self._transport.request('POST', 'invoice/pay', body)
        return Invoice.from_dict(raw.get('data') or {})

    def get_link(self, sid: str, invoice_id: int | str) -> FormLink:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('GET', 'invoice/link', body)
        return FormLink.from_dict(raw.get('data') or {})

    def list_items(self, sid: str, invoice_id: int | str) -> list[LineItem]:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('GET', 'invoice/items', body)
        items = raw.get('data', [])
        if isinstance(items, dict):
            items = list(items.values())
        return [LineItem.from_dict(item) for item in items if isinstance(item, dict)]

    def add_line_item(self, sid: str, invoice_id: int | str, attributes: dict[str, Any]) -> LineItem:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id} | attributes)
        raw = self._transport.request('POST', 'invoice/line-item/add', body)
        return LineItem.from_dict(raw.get('data') or {})

    def update_line_item(self, sid: str, line_item_id: int | str, attributes: dict[str, Any]) -> LineItem:
        body = self._envelope({'sid': sid, 'line_item_id': line_item_id} | attributes)
        raw = self._transport.request('PATCH', 'invoice/line-item/update', body)
        return LineItem.from_dict(raw.get('data') or {})

    def delete_line_item(self, sid: str, line_item_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'line_item_id': line_item_id})
        raw = self._transport.request('POST', 'invoice/line-item/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def create_item(self, sid: str, invoice_id: int | str, item_id: int | str) -> LineItem:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id, 'item_id': item_id})
        raw = self._transport.request('POST', 'invoice/item/create', body)
        return LineItem.from_dict(raw.get('data') or {})
