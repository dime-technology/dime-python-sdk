from __future__ import annotations

from ..data_objects.fund_release import FundReleaseResult
from ..data_objects.held_balance import HeldBalance
from ..data_objects.releasable_transactions import ReleasableTransactions
from .abstract_resource import AbstractResource


class Funds(AbstractResource):
    """
    Held-funds endpoints, for merchants on a tier that does not sweep their
    balance to the bank automatically. Every other merchant gets a
    :class:`ValidationException` (422), since there is nothing held.

    Reading requires ``funds:read``. Releasing requires ``funds:release`` and an
    affiliate key.
    """

    def balance(self, sid: str) -> HeldBalance:
        """The merchant's balance at the processor, and how much is releasable now."""
        raw = self._transport.request('GET', 'funds/balance', self._envelope({'sid': sid}))
        return HeldBalance.from_dict(raw.get('data') or {})

    def transactions(self, sid: str) -> ReleasableTransactions:
        """
        The payments that can be released now, and what each would pay out —
        the list to choose from when releasing by ``transaction_info_ids``.
        """
        raw = self._transport.request('GET', 'funds/transactions', self._envelope({'sid': sid}))
        return ReleasableTransactions.from_dict(raw.get('data') or {})

    def release(
        self,
        sid: str,
        idempotency_key: str,
        amount: str | float | None = None,
        transaction_info_ids: list[str] | None = None,
    ) -> FundReleaseResult:
        """
        Send part of the held balance to the merchant's bank account.

        Pass exactly one of ``amount`` (dollars) or ``transaction_info_ids`` (up
        to 100, from :meth:`transactions`; all or nothing). The amount is checked
        against a freshly calculated ``releasable`` and is never reduced to fit.

        Use a new ``idempotency_key`` for each intended release and reuse it when
        retrying: the same key returns the original release (``replayed``) rather
        than sending money twice.

        Check :attr:`FundRelease.status` on the result — ``released`` or
        ``unknown`` (no confirmation; it may have gone through). A declined
        release raises :class:`ValidationException` (422), with the failed
        release under ``get_response_body()['data']['release']``. A key reused
        for a different release, or a release already in flight for the
        merchant, raises :class:`ApiException` (409).
        """
        body = self._envelope({
            'sid': sid,
            'amount': amount,
            'transaction_info_ids': transaction_info_ids,
            'idempotency_key': idempotency_key,
        })
        raw = self._transport.request('POST', 'funds/release', body)
        return FundReleaseResult.from_dict(raw.get('data') or {})
