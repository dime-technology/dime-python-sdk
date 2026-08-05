from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import requests

from ..exceptions.connection_exception import ConnectionException
from .error_handler import ErrorHandler

if TYPE_CHECKING:
    from ..config import Config

SDK_VERSION = '1.2.0'


class Transport:
    def __init__(self, config: Config) -> None:
        self._config = config
        if config._session is not None:
            self._session = config._session
        else:
            self._session = requests.Session()
            self._session.headers.update({
                'Authorization': f'Bearer {config.token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Dime-Sdk': f'dime-python-sdk/{SDK_VERSION}',
            })

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self._config.base_uri() + path.lstrip('/')
        params = {k: v for k, v in (query or {}).items() if v is not None} or None

        attempt = 0

        while True:
            try:
                response = self._session.request(
                    method.upper(),
                    url,
                    json=body or None,
                    params=params,
                    timeout=self._config.timeout,
                )
            except requests.exceptions.RequestException as exc:
                if attempt < self._config.max_retries:
                    self._do_sleep(self._config.retry_base_delay * (2 ** attempt))
                    attempt += 1
                    continue
                raise ConnectionException(f'Could not reach the Dime API: {exc}') from exc

            if (response.status_code == 429 or response.status_code >= 500) and attempt < self._config.max_retries:
                self._do_sleep(self._retry_delay(attempt, response))
                attempt += 1
                continue

            ErrorHandler.check(response)
            return response.json()

    def _retry_delay(self, attempt: int, response: Any) -> float:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass
        return min(self._config.retry_base_delay * (2 ** attempt), 30.0)

    def _do_sleep(self, seconds: float) -> None:
        if self._config._sleep is not None:
            self._config._sleep(seconds)
        else:
            time.sleep(seconds)
