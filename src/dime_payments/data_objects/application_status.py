from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_string


@dataclass
class ApplicationStatus:
    """
    Where a merchant sits in onboarding.

    ``status`` is the headline: one of ``lead``, ``discovery``, ``proposal``,
    ``application_in_progress``, ``underwriting``, ``live``,
    ``cancellation_pending``, ``churned`` or ``declined`` (``None`` if onboarding
    has not started). ``application_status`` is the underlying application —
    ``draft``, ``pending_review``, ``submitted``, ``approved``,
    ``needs_documents``, ``failed`` or ``None`` — and is the field to read while
    ``status`` is ``underwriting``, since only ``needs_documents`` asks you to
    act. ``boarded`` is the ground truth for whether the merchant can take money.
    """

    sid: str | None = None
    name: str | None = None
    status: str | None = None
    application_status: str | None = None
    boarded: bool = False
    application_submitted_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ApplicationStatus':
        return cls(
            sid=arr_string(data, 'sid'),
            name=arr_string(data, 'name'),
            status=arr_string(data, 'status'),
            application_status=arr_string(data, 'application_status'),
            boarded=arr_bool(data, 'boarded'),
            application_submitted_at=arr_string(data, 'application_submitted_at'),
        )
