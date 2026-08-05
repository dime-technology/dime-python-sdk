from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_int, arr_object, arr_string
from .invoice_customer import InvoiceCustomer
from .line_item import LineItem


@dataclass
class RecurringInvoiceRun:
    """A summary of one invoice already emitted by a recurring template."""

    id: int | None = None
    invoice_number: str | None = None
    status: str | None = None
    total: str | None = None
    issue_date: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringInvoiceRun':
        return cls(
            id=arr_int(data, 'id'),
            invoice_number=arr_string(data, 'invoice_number'),
            status=arr_string(data, 'status'),
            total=arr_string(data, 'total'),
            issue_date=arr_string(data, 'issue_date'),
        )


@dataclass
class RecurringInvoice:
    """
    A recurring-invoice template. ``recurrence_schedule`` is one of Weekly,
    Biweekly, FirstFifteenth, Monthly or Yearly.
    """

    id: int | None = None
    status: str | None = None
    recurrence_schedule: str | None = None
    payment_terms: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    next_run_date: str | None = None
    last_run_date: str | None = None
    thank_you_note: str | None = None
    customer: InvoiceCustomer = field(default_factory=InvoiceCustomer)
    items: list[LineItem] = field(default_factory=list)
    upcoming_run_dates: list[str] = field(default_factory=list)
    invoices: list[RecurringInvoiceRun] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'RecurringInvoice':
        return cls(
            id=arr_int(data, 'id'),
            status=arr_string(data, 'status'),
            recurrence_schedule=arr_string(data, 'recurrence_schedule'),
            payment_terms=arr_string(data, 'payment_terms'),
            start_date=arr_string(data, 'start_date'),
            end_date=arr_string(data, 'end_date'),
            next_run_date=arr_string(data, 'next_run_date'),
            last_run_date=arr_string(data, 'last_run_date'),
            thank_you_note=arr_string(data, 'thank_you_note'),
            customer=InvoiceCustomer.from_dict(arr_object(data, 'customer')),
            items=[LineItem.from_dict(i) for i in arr_array(data, 'items') if isinstance(i, dict)],
            upcoming_run_dates=[str(d) for d in arr_array(data, 'upcoming_run_dates')],
            invoices=[RecurringInvoiceRun.from_dict(i) for i in arr_array(data, 'invoices') if isinstance(i, dict)],
        )
