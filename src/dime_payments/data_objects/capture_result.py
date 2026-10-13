from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string
from .message_result import MessageResult


@dataclass
class CaptureResult(MessageResult):
    """
    The response to a capture: what was taken, beside the confirmation message.

    ``transaction_id`` is the authorization's transaction number, as sent.
    ``authorized_amount`` is what the hold was for and ``captured_amount`` what
    was collected; a partial capture releases the difference. Amounts are the
    API's two-decimal strings (e.g. ``"95.00"``). ``status`` is ``captured`` and
    ``captured_at`` is an ISO 8601 timestamp.

    It is a :class:`MessageResult`, so ``message`` still reads as before. The
    extra fields are ``None`` against an API that predates them.
    """

    transaction_id: str | None = None
    authorized_amount: str | None = None
    captured_amount: str | None = None
    status: str | None = None
    captured_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CaptureResult':
        return cls(
            message=arr_string(data, 'message'),
            transaction_id=arr_string(data, 'transaction_id'),
            authorized_amount=arr_string(data, 'authorized_amount'),
            captured_amount=arr_string(data, 'captured_amount'),
            status=arr_string(data, 'status'),
            captured_at=arr_string(data, 'captured_at'),
        )
