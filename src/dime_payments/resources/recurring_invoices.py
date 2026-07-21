from __future__ import annotations

from typing import Any

from ..data_objects.recurring_invoice import RecurringInvoice
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class RecurringInvoices(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[RecurringInvoice]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'recurring-invoices', body, RecurringInvoice.from_dict)

    def show(self, sid: str, recurring_invoice_id: int | str) -> RecurringInvoice:
        body = self._envelope({'sid': sid, 'recurring_invoice_id': recurring_invoice_id})
        raw = self._transport.request('GET', 'recurring-invoice', body)
        return RecurringInvoice.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> RecurringInvoice:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'recurring-invoice/create', body)
        return RecurringInvoice.from_dict(raw.get('data') or {})

    def cancel(self, sid: str, recurring_invoice_id: int | str) -> RecurringInvoice:
        body = self._envelope({'sid': sid, 'recurring_invoice_id': recurring_invoice_id})
        raw = self._transport.request('POST', 'recurring-invoice/cancel', body)
        return RecurringInvoice.from_dict(raw.get('data') or {})
