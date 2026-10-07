from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import requests


class Config:
    DEFAULT_BASE_URL = 'https://app.dimepayments.com'
    VERSION = '1.4.1'

    def __init__(
        self,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_base_delay: float = 0.5,
        session: 'requests.Session | None' = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        self.token = token
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self._session = session
        self._sleep = sleep

    def base_uri(self) -> str:
        return self.base_url.rstrip('/') + '/api/'
