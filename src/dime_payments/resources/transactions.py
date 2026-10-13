from __future__ import annotations

import uuid
from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.tokenize_result import TokenizeResult
from ..data_objects.transaction import Transaction
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Transactions(AbstractResource):
    """
    The money-moving calls (charge_card, charge_card_token, charge_ach,
    authorize, capture, refund and void) each send an ``Idempotency-Key``, so
    the SDK's automatic retries cannot charge twice: a retry the API already
    processed returns the original response. Pass ``idempotency_key`` to reuse
    a key across your own retries; otherwise a new one is generated per call.
    A refused key raises :class:`IdempotencyException`.
    """

    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Transaction]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'transactions', body, Transaction.from_dict)

    def show(self, sid: str, identifier: dict[str, Any]) -> Transaction:
        raw = self._transport.request('GET', 'transaction', self._envelope({'sid': sid} | identifier))
        return Transaction.from_dict(raw.get('data') or {})

    def charge_card(
        self,
        sid: str,
        attributes: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request(
            'POST', 'transaction/charge-card', body, headers=self._idempotency_headers(idempotency_key),
        )
        return Transaction.from_dict(raw.get('data') or {})

    def charge_card_token(
        self,
        sid: str,
        attributes: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request(
            'POST', 'transaction/charge-card-token', body, headers=self._idempotency_headers(idempotency_key),
        )
        return Transaction.from_dict(raw.get('data') or {})

    def charge_ach(
        self,
        sid: str,
        attributes: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request(
            'POST', 'transaction/charge-ach', body, headers=self._idempotency_headers(idempotency_key),
        )
        return Transaction.from_dict(raw.get('data') or {})

    def authorize(
        self,
        sid: str,
        attributes: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Transaction:
        """
        Place a hold on a card without moving any money. ``amount`` is required;
        supply the card as a ``token`` or as raw ``card_number`` /
        ``expiration_date`` / ``cardholder_name`` / ``billing_address.zip``
        (raw card data requires PCI compliance).

        Collect with :meth:`capture`, or release the hold with :meth:`void`
        (``transaction_type`` ``CC``), passing the returned
        ``transaction_number`` in either case.
        """
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request(
            'POST', 'transaction/authorize', body, headers=self._idempotency_headers(idempotency_key),
        )
        return Transaction.from_dict(raw.get('data') or {})

    def capture(
        self,
        sid: str,
        transaction_id: int | str,
        amount: str | float | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> MessageResult:
        """
        Collect an authorization. ``transaction_id`` is the ``transaction_number``
        :meth:`authorize` returned. Omit ``amount`` to capture the full hold.

        An authorization can be captured once: a partial capture settles that
        amount and releases the rest back to the cardholder.
        """
        body = self._envelope({
            'sid': sid,
            'transaction_id': transaction_id,
            'amount': amount,
        })
        raw = self._transport.request(
            'POST', 'transaction/capture', body, headers=self._idempotency_headers(idempotency_key),
        )
        return MessageResult.from_dict(raw.get('data') or raw)

    def tokenize_card(self, sid: str, attributes: dict[str, Any] | None = None) -> TokenizeResult:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/tokenize-card', body)
        return TokenizeResult.from_dict(raw.get('data') or {})

    def refund(
        self,
        sid: str,
        attributes: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> MessageResult:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request(
            'POST', 'transaction/refund', body, headers=self._idempotency_headers(idempotency_key),
        )
        return MessageResult.from_dict(raw.get('data') or raw)

    def void(
        self,
        sid: str,
        transaction_type: str,
        transaction_id: int | str,
        *,
        idempotency_key: str | None = None,
    ) -> MessageResult:
        body = self._envelope({
            'sid': sid,
            'transaction_type': transaction_type,
            'transaction_id': transaction_id,
        })
        raw = self._transport.request(
            'PATCH', 'transaction/void', body, headers=self._idempotency_headers(idempotency_key),
        )
        return MessageResult.from_dict(raw.get('data') or raw)

    def _idempotency_headers(self, idempotency_key: str | None) -> dict[str, str]:
        """
        The key is fixed here, once per call, so every automatic retry of the
        request carries the same one.
        """
        return {'Idempotency-Key': idempotency_key if idempotency_key is not None else str(uuid.uuid4())}
