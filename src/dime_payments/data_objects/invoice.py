from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_int, arr_string
from .line_item import LineItem


@dataclass
class Invoice:
    id: int | None = None
    sid: str | None = None
    invoice_number: str | None = None
    customer_uuid: str | None = None
    status: str | None = None
    due_date: str | None = None
    notes: str | None = None
    subtotal: str | None = None
    total: str | None = None
    amount_paid: str | None = None
    amount_due: str | None = None
    link: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    sent_at: str | None = None
    paid_at: str | None = None
    voided_at: str | None = None
    line_items: list[LineItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Invoice':
        raw_items = data.get('line_items', [])
        if isinstance(raw_items, dict):
            raw_items = list(raw_items.values())
        line_items = [LineItem.from_dict(i) for i in raw_items if isinstance(i, dict)]

        return cls(
            id=arr_int(data, 'id'),
            sid=arr_string(data, 'sid'),
            invoice_number=arr_string(data, 'invoice_number'),
            customer_uuid=arr_string(data, 'customer_uuid'),
            status=arr_string(data, 'status'),
            due_date=arr_string(data, 'due_date'),
            notes=arr_string(data, 'notes'),
            subtotal=arr_string(data, 'subtotal'),
            total=arr_string(data, 'total'),
            amount_paid=arr_string(data, 'amount_paid'),
            amount_due=arr_string(data, 'amount_due'),
            link=arr_string(data, 'link'),
            created_at=arr_string(data, 'created_at'),
            updated_at=arr_string(data, 'updated_at'),
            sent_at=arr_string(data, 'sent_at'),
            paid_at=arr_string(data, 'paid_at'),
            voided_at=arr_string(data, 'voided_at'),
            line_items=line_items,
        )
