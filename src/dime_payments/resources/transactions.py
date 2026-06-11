from __future__ import annotations

from typing import Any

from ..data_objects.message_result import MessageResult
from ..data_objects.tokenize_result import TokenizeResult
from ..data_objects.transaction import Transaction
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Transactions(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Transaction]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'transactions', body, Transaction.from_dict)

    def show(self, sid: str, identifier: dict[str, Any]) -> Transaction:
        raw = self._transport.request('GET', 'transaction', self._envelope({'sid': sid} | identifier))
        return Transaction.from_dict(raw.get('data') or {})

    def charge_card(self, sid: str, attributes: dict[str, Any] | None = None) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/charge-card', body)
        return Transaction.from_dict(raw.get('data') or {})

    def charge_card_token(self, sid: str, attributes: dict[str, Any] | None = None) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/charge-card-token', body)
        return Transaction.from_dict(raw.get('data') or {})

    def charge_ach(self, sid: str, attributes: dict[str, Any] | None = None) -> Transaction:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/charge-ach', body)
        return Transaction.from_dict(raw.get('data') or {})

    def tokenize_card(self, sid: str, attributes: dict[str, Any] | None = None) -> TokenizeResult:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/tokenize-card', body)
        return TokenizeResult.from_dict(raw.get('data') or {})

    def refund(self, sid: str, attributes: dict[str, Any] | None = None) -> MessageResult:
        body = self._envelope({'sid': sid} | (attributes or {}))
        raw = self._transport.request('POST', 'transaction/refund', body)
        return MessageResult.from_dict(raw.get('data') or raw)

    def void(self, sid: str, transaction_type: str, transaction_id: int | str) -> MessageResult:
        body = self._envelope({
            'sid': sid,
            'transaction_type': transaction_type,
            'transaction_id': transaction_id,
        })
        raw = self._transport.request('PATCH', 'transaction/void', body)
        return MessageResult.from_dict(raw.get('data') or raw)
