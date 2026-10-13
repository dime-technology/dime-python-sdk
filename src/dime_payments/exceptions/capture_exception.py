from typing import Any

from .api_exception import ApiException
from .validation_exception import ValidationException


class CaptureException(ApiException, ValidationException):
    """
    A capture the API refused, with the reason as a machine-readable code.

    ``error_code`` is one of ``not_found``, ``already_captured``, ``voided``,
    ``refunded``, ``authorization_declined``, ``not_an_authorization``,
    ``amount_exceeds_authorization`` or ``processor_declined``; an unfamiliar
    code from a newer API is passed through as given. Several codes share one
    message ("Transaction is not an open authorization."), so branch on the
    code, not the message.

    ``reason`` is set on ``processor_declined`` only: the explanation given when
    the capture was refused. An expired authorization arrives this way too,
    since an issuer drops an uncaptured hold without notice.

    Nothing was captured. It is also a :class:`ValidationException`, which is
    what a refused capture raised before 1.6.0, so existing handlers still
    catch it. A field validation error (an ``errors`` object) still raises a
    plain :class:`ValidationException`.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        reason: str | None = None,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self.error_code = error_code
        self.reason = reason

    def get_error_code(self) -> str:
        return self.error_code

    def get_reason(self) -> str | None:
        return self.reason
