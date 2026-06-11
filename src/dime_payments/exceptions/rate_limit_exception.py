from typing import Any

from .dime_exception import DimeException


class RateLimitException(DimeException):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self._retry_after = retry_after

    def get_retry_after(self) -> float | None:
        return self._retry_after
