from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class InvoiceLink:
    """The public payment link for an invoice."""

    public_url: str | None = None
    token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoiceLink':
        return cls(
            public_url=arr_string(data, 'public_url'),
            token=arr_string(data, 'token'),
        )
