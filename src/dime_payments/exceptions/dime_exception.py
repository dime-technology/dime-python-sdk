from typing import Any


class DimeException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body: dict[str, Any] = response_body or {}

    def get_status_code(self) -> int | None:
        return self.status_code

    def get_response_body(self) -> dict[str, Any]:
        return self.response_body
