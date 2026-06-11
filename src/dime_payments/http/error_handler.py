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
            msg = message if isinstance(message, str) else f'Validation failed ({status})'
            raise ValidationException(msg, status_code=status, response_body=body)

        if status == 401:
            msg = body.get('message', 'Unauthenticated')
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
            msg = body.get('message', 'Too many requests')
            raise RateLimitException(str(msg), status_code=status, response_body=body, retry_after=retry_after)

        if status >= 500:
            msg = body.get('message', 'Server error')
            raise ServerException(str(msg), status_code=status, response_body=body)

        msg = body.get('message', f'HTTP {status}')
        raise ApiException(str(msg), status_code=status, response_body=body)
