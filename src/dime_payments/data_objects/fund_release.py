from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_bool, arr_int, arr_object, arr_string


@dataclass
class FundRelease:
    """
    A request to pay out held funds.

    ``status`` is ``released`` (sent), ``failed`` (declined; nothing moved) or
    ``unknown`` (no confirmation came back, so it may have gone through — its
    amount stays held back from ``releasable`` until it is reconciled).
    ``transaction_info_ids`` is empty when the release was requested by amount.
    """

    id: int | None = None
    amount: str | None = None
    fee: str | None = None
    status: str | None = None
    status_label: str | None = None
    idempotency_key: str | None = None
    transaction_info_ids: list[str] = field(default_factory=list)
    failure_reason: str | None = None
    requested_at: str | None = None
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FundRelease':
        return cls(
            id=arr_int(data, 'id'),
            amount=arr_string(data, 'amount'),
            fee=arr_string(data, 'fee'),
            status=arr_string(data, 'status'),
            status_label=arr_string(data, 'status_label'),
            idempotency_key=arr_string(data, 'idempotency_key'),
            transaction_info_ids=[str(t) for t in arr_array(data, 'transaction_info_ids') if t is not None],
            failure_reason=arr_string(data, 'failure_reason'),
            requested_at=arr_string(data, 'requested_at'),
            completed_at=arr_string(data, 'completed_at'),
        )


@dataclass
class FundReleaseResult:
    """
    The response to :meth:`Funds.release`. ``replayed`` is true when the
    ``idempotency_key`` had been used before and the original release is being
    returned rather than a new one sent.
    """

    sid: str | None = None
    replayed: bool = False
    release: FundRelease = field(default_factory=FundRelease)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FundReleaseResult':
        return cls(
            sid=arr_string(data, 'sid'),
            replayed=arr_bool(data, 'replayed'),
            release=FundRelease.from_dict(arr_object(data, 'release')),
        )
