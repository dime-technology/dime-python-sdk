from __future__ import annotations

from typing import Any

from ..data_objects.invoice import Invoice
from ..data_objects.invoice_item import InvoiceItem
from ..data_objects.invoice_link import InvoiceLink
from ..data_objects.message_result import MessageResult
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Invoices(AbstractResource):
    """
    Invoice endpoints.

    Every method takes the merchant ``sid`` explicitly; remaining fields go in an
    ``attributes`` dict. Identify the customer with ``customer_uuid`` — the same
    identifier the customer, payment-method and address endpoints use, and the
    only one :class:`Customer` exposes. ``customer_id`` is still accepted for
    integrations written against the original contract; supply exactly one.

    Line-item and invoice mutations return the refreshed invoice, so the caller
    always sees recalculated totals rather than a detached fragment.
    """

    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Invoice]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'invoices', body, Invoice.from_dict)

    def show(self, sid: str, invoice_id: int | str) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('GET', 'invoice', body)
        return Invoice.from_dict(raw.get('data') or {})

    def create(self, sid: str, attributes: dict[str, Any]) -> Invoice:
        """
        Create a draft invoice. Requires ``customer_uuid`` (or ``customer_id``),
        ``customer_name``, ``customer_email``, ``payment_terms``
        (``due_on_receipt`` | ``net_15`` | ``net_30`` | ``net_60``) and at least
        one entry in ``lines``, each referencing a Merchant ``item_id``.
        """
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'invoice/create', body)
        return Invoice.from_dict(raw.get('data') or {})

    def update(self, sid: str, invoice_id: int | str, attributes: dict[str, Any]) -> Invoice:
        """Update a draft invoice. Passing ``lines`` replaces the existing lines."""
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id} | attributes)
        raw = self._transport.request('PATCH', 'invoice/update', body)
        return Invoice.from_dict(raw.get('data') or {})

    def delete(self, sid: str, invoice_id: int | str) -> MessageResult:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/delete', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def send(self, sid: str, invoice_id: int | str) -> Invoice:
        """Email the invoice and advance it to Sent."""
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('POST', 'invoice/send', body)
        return Invoice.from_dict(raw.get('data') or {})

    def mark_sent(self, sid: str, invoice_id: int | str) -> Invoice:
        """Activate a draft for payment without emailing it."""
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

    def pay(self, sid: str, invoice_id: int | str, attributes: dict[str, Any]) -> Invoice:
        """
        Record a merchant-initiated (MOTO) payment against an open invoice.

        ``payment_type`` is required and is either ``cc`` or ``ach``. For a card,
        pass a stored ``token`` or raw ``cardholder_name`` / ``card_number`` /
        ``expiration_date``; for ACH, pass ``routing_number`` /
        ``account_number`` / ``account_type`` / ``account_name``. Omit ``amount``
        to pay the full balance.
        """
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id} | attributes)
        raw = self._transport.request('POST', 'invoice/pay', body)
        return Invoice.from_dict(raw.get('data') or {})

    def get_link(self, sid: str, invoice_id: int | str) -> InvoiceLink:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id})
        raw = self._transport.request('GET', 'invoice/link', body)
        return InvoiceLink.from_dict(raw.get('data') or {})

    def list_items(self, sid: str) -> list[InvoiceItem]:
        """
        List the Merchant's items (funds/designations) that line items can
        reference. Scoped to the merchant, not to a single invoice — an
        invoice's own lines are on :attr:`Invoice.items`.
        """
        body = self._envelope({'sid': sid})
        raw = self._transport.request('GET', 'invoice/items', body)
        items = raw.get('data', [])
        if isinstance(items, dict):
            items = list(items.values())
        return [InvoiceItem.from_dict(item) for item in items if isinstance(item, dict)]

    def create_item(self, sid: str, attributes: dict[str, Any]) -> InvoiceItem:
        """
        Create an invoicing-only Merchant item. ``name`` is required;
        ``description``, ``price`` and ``tax_deductible`` are optional.
        """
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('POST', 'invoice/item/create', body)
        return InvoiceItem.from_dict(raw.get('data') or {})

    def add_line_item(self, sid: str, invoice_id: int | str, attributes: dict[str, Any]) -> Invoice:
        body = self._envelope({'sid': sid, 'invoice_id': invoice_id} | attributes)
        raw = self._transport.request('POST', 'invoice/line-item/add', body)
        return Invoice.from_dict(raw.get('data') or {})

    def update_line_item(
        self,
        sid: str,
        invoice_id: int | str,
        line_item_id: int | str,
        attributes: dict[str, Any],
    ) -> Invoice:
        body = self._envelope(
            {'sid': sid, 'invoice_id': invoice_id, 'line_item_id': line_item_id} | attributes
        )
        raw = self._transport.request('PATCH', 'invoice/line-item/update', body)
        return Invoice.from_dict(raw.get('data') or {})

    def delete_line_item(self, sid: str, invoice_id: int | str, line_item_id: int | str) -> Invoice:
        body = self._envelope(
            {'sid': sid, 'invoice_id': invoice_id, 'line_item_id': line_item_id}
        )
        raw = self._transport.request('POST', 'invoice/line-item/delete', body)
        return Invoice.from_dict(raw.get('data') or {})
