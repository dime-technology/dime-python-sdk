from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_object, arr_string


@dataclass
class CoverFeeQuote:
    """
    The processing fee a cover-fee invoice adds on top of what the customer pays,
    quoted for both payment methods.

    Present on an :class:`Invoice` only when ``cover_fee_required`` is true. The fee
    is NOT a line item and is NOT part of the invoice's ``total``: the merchant is
    owed ``total``, and the customer is charged ``total`` plus this fee. Card and
    ACH rates differ, so the amount depends on how the customer chooses to pay —
    ``cc_total`` is the higher of the two and what the invoice and its emails lead
    with.

    ``basis`` names what the quote was computed against — currently always
    ``balance``, the amount still outstanding. Paying a partial amount re-quotes the
    fee against that amount, so treat these as a quote for settling in full today
    rather than a fixed charge.

    Money is kept as strings, consistent with the rest of the SDK, to avoid float
    rounding.
    """

    basis: str | None = None
    base: str | None = None
    cc_fee: str | None = None
    cc_total: str | None = None
    ach_fee: str | None = None
    ach_total: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CoverFeeQuote':
        cc = arr_object(data, 'cc')
        ach = arr_object(data, 'ach')

        return cls(
            basis=arr_string(data, 'basis'),
            base=arr_string(data, 'base'),
            cc_fee=arr_string(cc, 'fee'),
            cc_total=arr_string(cc, 'total'),
            ach_fee=arr_string(ach, 'fee'),
            ach_total=arr_string(ach, 'total'),
        )
