from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import requests

from ..exceptions.connection_exception import ConnectionException
from .error_handler import ErrorHandler

if TYPE_CHECKING:
    from ..config import Config

SDK_VERSION = '1.4.0'


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
        files: list[tuple[str, tuple[str, bytes, str]]] | None = None,
    ) -> dict[str, Any]:
        """
        Send a request and return the decoded JSON body.

        ``body`` is sent as JSON, unless ``files`` is given: then the request is
        ``multipart/form-data``, with ``body`` flattened into bracketed form fields
        (``data[sid]``) and each ``(field, (filename, content, content_type))`` in
        ``files`` attached as a file part.
        """
        url = self._config.base_uri() + path.lstrip('/')
        params = {k: v for k, v in (query or {}).items() if v is not None} or None

        payload: dict[str, Any]
        if files is None:
            payload = {'json': body or None}
        else:
            # Dropping the session's JSON Content-Type lets requests set the
            # multipart one, boundary included.
            payload = {
                'data': self._form_fields(body or {}),
                'files': files,
                'headers': {'Content-Type': None},
            }

        attempt = 0

        while True:
            try:
                response = self._session.request(
                    method.upper(),
                    url,
                    params=params,
                    timeout=self._config.timeout,
                    **payload,
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

    def _form_fields(self, values: dict[Any, Any], prefix: str = '') -> list[tuple[str, str]]:
        """Flatten nested values into the bracketed field names PHP parses into arrays."""
        fields: list[tuple[str, str]] = []
        for key, value in values.items():
            name = f'{prefix}[{key}]' if prefix else str(key)
            if value is None:
                continue
            if isinstance(value, dict):
                fields.extend(self._form_fields(value, name))
            elif isinstance(value, (list, tuple)):
                fields.extend(self._form_fields(dict(enumerate(value)), name))
            elif isinstance(value, bool):
                fields.append((name, '1' if value else '0'))
            else:
                fields.append((name, str(value)))
        return fields

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
