from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_bool, arr_int, arr_object, arr_string
from .cover_fee_quote import CoverFeeQuote
from .invoice_customer import InvoiceCustomer
from .invoice_event import InvoiceEvent
from .invoice_payment import InvoicePayment
from .line_item import LineItem


@dataclass
class Invoice:
    """
    A full invoice as returned by the show, create, update and action endpoints.

    Money fields arrive as dollar amounts and are kept as strings, consistent
    with the rest of the SDK, to avoid float rounding.

    When ``cover_fee_required`` is set the customer must also pay the processing
    fee, which is reported on :attr:`cover_fee_quote` rather than included in
    ``total`` — so what settles is more than what the invoice says.
    """

    id: int | None = None
    token: str | None = None
    invoice_number: str | None = None
    status: str | None = None
    payment_terms: str | None = None
    issue_date: str | None = None
    due_date: str | None = None
    is_overdue: bool = False
    subtotal: str | None = None
    total: str | None = None
    amount_paid: str | None = None
    balance: str | None = None
    allow_partial_payment: bool = False
    cover_fee_required: bool = False
    cover_fee_quote: CoverFeeQuote | None = None
    thank_you_note: str | None = None
    public_url: str | None = None
    customer: InvoiceCustomer = field(default_factory=InvoiceCustomer)
    items: list[LineItem] = field(default_factory=list)
    payments: list[InvoicePayment] = field(default_factory=list)
    events: list[InvoiceEvent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Invoice':
        return cls(
            id=arr_int(data, 'id'),
            token=arr_string(data, 'token'),
            invoice_number=arr_string(data, 'invoice_number'),
            status=arr_string(data, 'status'),
            payment_terms=arr_string(data, 'payment_terms'),
            issue_date=arr_string(data, 'issue_date'),
            due_date=arr_string(data, 'due_date'),
            is_overdue=arr_bool(data, 'is_overdue'),
            subtotal=arr_string(data, 'subtotal'),
            total=arr_string(data, 'total'),
            amount_paid=arr_string(data, 'amount_paid'),
            balance=arr_string(data, 'balance'),
            allow_partial_payment=arr_bool(data, 'allow_partial_payment'),
            cover_fee_required=arr_bool(data, 'cover_fee_required'),
            cover_fee_quote=(
                CoverFeeQuote.from_dict(data['cover_fee_quote'])
                if isinstance(data.get('cover_fee_quote'), dict)
                else None
            ),
            thank_you_note=arr_string(data, 'thank_you_note'),
            public_url=arr_string(data, 'public_url'),
            customer=InvoiceCustomer.from_dict(arr_object(data, 'customer')),
            items=[LineItem.from_dict(i) for i in arr_array(data, 'items') if isinstance(i, dict)],
            payments=[InvoicePayment.from_dict(p) for p in arr_array(data, 'payments') if isinstance(p, dict)],
            events=[InvoiceEvent.from_dict(e) for e in arr_array(data, 'events') if isinstance(e, dict)],
        )
