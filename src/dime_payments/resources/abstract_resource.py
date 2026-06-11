from __future__ import annotations

from typing import Any, Callable, TypeVar

from ..http.transport import Transport
from ..pagination.cursor_page import CursorPage

T = TypeVar('T')


class AbstractResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def _envelope(
        self,
        data: dict[str, Any] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if data:
            pruned = {k: v for k, v in data.items() if v is not None}
            if pruned:
                body['data'] = pruned
        if filters:
            pruned_f = {k: v for k, v in filters.items() if v is not None}
            if pruned_f:
                body['filters'] = pruned_f
        return body

    def _paginate(
        self,
        method: str,
        path: str,
        body: dict[str, Any],
        mapper: Callable[[dict[str, Any]], T],
        query: dict[str, Any] | None = None,
    ) -> CursorPage[T]:
        def fetcher(cursor: str | None) -> CursorPage[T]:
            return self._paginate(method, path, body, mapper, {'cursor': cursor})

        response = self._transport.request(method, path, body, query)

        raw_data = response.get('data', [])
        if isinstance(raw_data, dict):
            raw_data = list(raw_data.values())

        items = [mapper(item) for item in raw_data if isinstance(item, dict)]
        return CursorPage.from_response(items, response, fetcher)
