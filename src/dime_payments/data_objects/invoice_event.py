from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class InvoiceEvent:
    """An entry in an invoice's history (created, sent, paid, voided, ...)."""

    type: str | None = None
    label: str | None = None
    description: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'InvoiceEvent':
        return cls(
            type=arr_string(data, 'type'),
            label=arr_string(data, 'label'),
            description=arr_string(data, 'description'),
            created_at=arr_string(data, 'created_at'),
        )
