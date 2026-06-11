from typing import Any

from .dime_exception import DimeException


class ValidationException(DimeException):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
        errors: dict[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self.errors: dict[str, list[str]] = errors or {}

    def get_errors(self) -> dict[str, list[str]]:
        return self.errors

    def first_error(self) -> str | None:
        for messages in self.errors.values():
            if messages:
                return messages[0]
        return None
