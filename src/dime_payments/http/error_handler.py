from typing import Any

from ..exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    PermissionDeniedException,
    RateLimitException,
    ServerException,
    ValidationException,
)


class ErrorHandler:
    @staticmethod
    def check(response: Any) -> None:
        status: int = response.status_code
        if 200 <= status < 300:
            return

        try:
            body: dict[str, Any] = response.json()
            if not isinstance(body, dict):
                body = {}
        except Exception:
            body = {}

        if status in (400, 422):
            errors = body.get('errors')
            if isinstance(errors, dict):
                raise ValidationException('Validation failed', status_code=status, response_body=body, errors=errors)
            message = body.get('message')
            if isinstance(message, dict):
                raise ValidationException('Validation failed', status_code=status, response_body=body, errors=message)
            msg = ErrorHandler._message(body) or f'Validation failed ({status})'
            raise ValidationException(msg, status_code=status, response_body=body)

        if status == 401:
            msg = ErrorHandler._message(body) or 'Unauthenticated'
            raise AuthenticationException(str(msg), status_code=status, response_body=body)

        if status == 403:
            data_section = body.get('data') or {}
            msg = (
                body.get('message')
                or (data_section.get('message') if isinstance(data_section, dict) else None)
                or 'Forbidden'
            )
            raise PermissionDeniedException(str(msg), status_code=status, response_body=body)

        if status == 404:
            data_section = body.get('data') or {}
            msg = (
                body.get('message')
                or (data_section.get('message') if isinstance(data_section, dict) else None)
                or 'Not found'
            )
            raise NotFoundException(str(msg), status_code=status, response_body=body)

        if status == 429:
            retry_after_hdr = response.headers.get('Retry-After')
            retry_after: float | None = None
            if retry_after_hdr:
                try:
                    retry_after = float(retry_after_hdr)
                except (ValueError, TypeError):
                    pass
            msg = ErrorHandler._message(body) or 'Too many requests'
            raise RateLimitException(str(msg), status_code=status, response_body=body, retry_after=retry_after)

        if status >= 500:
            msg = ErrorHandler._message(body) or 'Server error'
            raise ServerException(str(msg), status_code=status, response_body=body)

        msg = ErrorHandler._message(body) or f'HTTP {status}'
        raise ApiException(str(msg), status_code=status, response_body=body)

    @staticmethod
    def _message(body: dict[str, Any]) -> str | None:
        """The API's error message, which it sends either at the top level or under ``data``."""
        message = body.get('message')
        if isinstance(message, str) and message:
            return message
        data_section = body.get('data')
        if isinstance(data_section, dict):
            nested = data_section.get('message')
            if isinstance(nested, str) and nested:
                return nested
        return None
