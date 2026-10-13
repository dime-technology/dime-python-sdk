from .api_exception import ApiException


class IdempotencyException(ApiException):
    """
    The API refused an ``Idempotency-Key``: 422 when the key was already used
    for a different request, 409 when a request with the key is still in
    progress (or did not finish).
    """
