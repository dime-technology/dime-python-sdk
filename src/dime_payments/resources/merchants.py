from __future__ import annotations

from typing import Any

from ..data_objects.application_status import ApplicationStatus
from ..data_objects.form_link import FormLink
from ..data_objects.merchant import Merchant
from ..pagination.cursor_page import CursorPage
from .abstract_resource import AbstractResource


class Merchants(AbstractResource):
    def list(self, filters: dict[str, Any] | None = None) -> CursorPage[Merchant]:
        body = self._envelope({}, filters or {})
        return self._paginate('GET', 'merchant/list', body, Merchant.from_dict)

    def show(self, sid: str) -> Merchant:
        raw = self._transport.request('GET', 'merchant/show', self._envelope({'sid': sid}))
        return Merchant.from_dict(raw.get('data') or {})

    def create(self, attributes: dict[str, Any]) -> Merchant:
        raw = self._transport.request('POST', 'merchant/create', self._envelope(attributes))
        return Merchant.from_dict(raw.get('data') or {})

    def update(self, sid: str, attributes: dict[str, Any]) -> Merchant:
        body = self._envelope({'sid': sid} | attributes)
        raw = self._transport.request('PATCH', 'merchant/update', body)
        return Merchant.from_dict(raw.get('data') or {})

    def get_form_link(self, sid: str) -> FormLink:
        raw = self._transport.request('GET', 'merchant/get-form-link', self._envelope({'sid': sid}))
        return FormLink.from_dict(raw.get('data') or {})

    def application_status(self, sid: str) -> ApplicationStatus:
        """
        Where the merchant sits in onboarding — use it to follow up an application
        sent with :meth:`get_form_link`. Prefer the ``application_status_changed``
        webhook, which carries the same fields, and poll only to reconcile.
        """
        raw = self._transport.request('GET', 'merchant/application-status', self._envelope({'sid': sid}))
        return ApplicationStatus.from_dict(raw.get('data') or {})
