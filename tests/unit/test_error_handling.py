import pytest
from unittest.mock import MagicMock

from dime_payments import (
    ApiException,
    AuthenticationException,
    ConnectionException,
    DimeException,
    NotFoundException,
    PermissionDeniedException,
    RateLimitException,
    ServerException,
    ValidationException,
    Client,
)
from dime_payments.config import Config
from tests.helpers import fake_client


def test_validation_exception_422_with_errors_map():
    client, _ = fake_client([{
        'status': 422,
        'body': {'errors': {'data.amount': ['The amount field is required.']}},
    }])
    with pytest.raises(ValidationException) as exc_info:
        client.transactions.charge_card('000010', {})
    e = exc_info.value
    assert e.status_code == 422
    assert e.get_errors()['data.amount'][0] == 'The amount field is required.'
    assert e.first_error() == 'The amount field is required.'


def test_validation_exception_400_with_message_map():
    client, _ = fake_client([{
        'status': 400,
        'body': {'message': {'field': ['Invalid value']}},
    }])
    with pytest.raises(ValidationException):
        client.addresses.create('s', 'u', {})


def test_authentication_exception_401():
    client, _ = fake_client([{'status': 401, 'body': {'message': 'Unauthenticated.'}}])
    with pytest.raises(AuthenticationException) as exc_info:
        client.transactions.list('000010')
    assert exc_info.value.status_code == 401


def test_permission_denied_exception_403():
    client, _ = fake_client([{'status': 403, 'body': {'data': {'message': 'Not authorized.'}}}])
    with pytest.raises(PermissionDeniedException):
        client.transactions.list('000010')


def test_not_found_exception_404():
    client, _ = fake_client([{'status': 404, 'body': {'data': {'message': 'Not found.'}}}])
    with pytest.raises(NotFoundException):
        client.merchants.show('bad-sid')


def test_rate_limit_exception_with_retry_after():
    client, _ = fake_client([
        {'status': 429, 'body': {'message': 'Too many requests.'}, 'headers': {'Retry-After': '30'}},
        {'status': 429, 'body': {'message': 'Too many requests.'}, 'headers': {'Retry-After': '30'}},
        {'status': 429, 'body': {'message': 'Too many requests.'}, 'headers': {'Retry-After': '30'}},
    ])
    with pytest.raises(RateLimitException) as exc_info:
        client.transactions.list('000010')
    assert exc_info.value.get_retry_after() == 30.0


def test_server_exception_500():
    client, _ = fake_client([
        {'status': 500, 'body': {'message': 'Internal server error'}},
        {'status': 500, 'body': {'message': 'Internal server error'}},
        {'status': 500, 'body': {'message': 'Internal server error'}},
    ])
    with pytest.raises(ServerException):
        client.transactions.list('000010')


def test_api_exception_for_other_non_2xx():
    client, _ = fake_client([{'status': 409, 'body': {'message': 'Conflict'}}])
    with pytest.raises(ApiException):
        client.transactions.list('000010')


def test_all_exceptions_are_dime_exception():
    for status in [401, 403, 404]:
        client, _ = fake_client([{'status': status, 'body': {}}])
        with pytest.raises(DimeException):
            client.transactions.list('000010')


def test_connection_exception_when_request_fails():
    import requests as req_lib

    mock_session = MagicMock()
    mock_session.request.side_effect = req_lib.exceptions.ConnectionError('Failed to connect')
    config = Config(token='test-token', session=mock_session, sleep=lambda _: None, max_retries=0)
    client = Client(config)

    with pytest.raises(ConnectionException):
        client.transactions.list('000010')
