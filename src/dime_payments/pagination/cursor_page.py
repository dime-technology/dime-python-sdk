from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, TypeVar

T = TypeVar('T')
PageFetcher = Callable[[str | None], 'CursorPage[T]']


class CursorPage(Generic[T]):
    def __init__(
        self,
        data: list[T],
        next_cursor: str | None = None,
        prev_cursor: str | None = None,
        per_page: int | None = None,
        path: str | None = None,
        fetcher: PageFetcher | None = None,
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.prev_cursor = prev_cursor
        self.per_page = per_page
        self.path = path
        self._fetcher = fetcher

    def has_more(self) -> bool:
        return self.next_cursor is not None and self._fetcher is not None

    def next(self) -> CursorPage[T] | None:
        if not self.has_more():
            return None
        assert self._fetcher is not None
        return self._fetcher(self.next_cursor)

    def auto_paging(self) -> Iterator[T]:
        page: CursorPage[T] | None = self
        while page is not None:
            # Yield items individually (not yield from) so indices stay sequential.
            for item in page.data:
                yield item
            page = page.next()

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    @classmethod
    def from_response(
        cls,
        items: list[T],
        response: dict[str, Any],
        fetcher: PageFetcher,
    ) -> CursorPage[T]:
        meta = response.get('meta') or {}
        if not isinstance(meta, dict):
            meta = {}

        next_cursor = meta.get('next_cursor')
        prev_cursor = meta.get('prev_cursor')
        per_page = meta.get('per_page')
        path = meta.get('path')

        return cls(
            data=items,
            next_cursor=next_cursor if isinstance(next_cursor, str) and next_cursor else None,
            prev_cursor=prev_cursor if isinstance(prev_cursor, str) and prev_cursor else None,
            per_page=int(per_page) if isinstance(per_page, (int, float, str)) and str(per_page).isdigit() else None,
            path=path if isinstance(path, str) else None,
            fetcher=fetcher,
        )
