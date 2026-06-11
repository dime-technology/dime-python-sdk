from __future__ import annotations

from typing import Any

from ..data_objects.deposit import Deposit
from ..data_objects.deposit_group import DepositGroup
from ..data_objects.deposit_with_transactions import DepositWithTransactions
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Deposits(AbstractResource):
    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Deposit]:
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'deposit/list', body, Deposit.from_dict)

    def list_with_transactions(self, sid: str, filters: dict[str, Any]) -> DepositGroup:
        raw = self._transport.request(
            'GET',
            'deposit/list-with-trans',
            self._envelope({'sid': sid}, filters),
        )
        return DepositGroup.from_dict(raw.get('data') or {})

    def show(self, sid: str, identifier: dict[str, Any]) -> DepositWithTransactions:
        raw = self._transport.request(
            'GET',
            'deposit/show',
            self._envelope({'sid': sid} | identifier),
        )
        return DepositWithTransactions.from_dict(raw.get('data') or {})
