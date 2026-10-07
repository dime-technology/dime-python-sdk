from __future__ import annotations

from typing import Any

from ..data_objects.chargeback import Chargeback
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Chargebacks(AbstractResource):
    """
    Chargeback endpoints. Requires the ``chargeback:read`` ability.

    Chargebacks reach Dime in a once-daily file from the processor, so these
    reflect the latest import rather than live dispute activity. Use the
    ``chargeback_opened`` / ``chargeback_updated`` / ``chargeback_resolved``
    webhooks to hear about changes, and these endpoints to reconcile.
    """

    def list(self, sid: str, filters: dict[str, Any] | None = None) -> CursorPage[Chargeback]:
        """
        List a merchant's chargebacks, oldest first.

        ``filters`` takes ``start_date`` and ``end_date`` together (UTC,
        ``YYYY-mm-dd HH:MM:SS``) and ``representment_status``. A merchant with
        no chargebacks returns an empty page, not an error.
        """
        body = self._envelope({'sid': sid}, filters or {})
        return self._paginate('GET', 'chargeback/list', body, Chargeback.from_dict)

    def show(self, sid: str, transaction_info_id: str) -> Chargeback:
        body = self._envelope({'sid': sid, 'transaction_info_id': transaction_info_id})
        raw = self._transport.request('GET', 'chargeback/show', body)
        return Chargeback.from_dict(raw.get('data') or {})
