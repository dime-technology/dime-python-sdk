import uuid
from unittest.mock import MagicMock

import pytest
import requests

from dime_payments import (
    ApiException,
    Client,
    IdempotencyException,
    ValidationException,
)
from dime_payments.config import Config
from tests.helpers import fake_client, make_mock_response

TXN_RESPONSE = {'status': 200, 'body': {'data': {'transaction_status': 'Success', 'amount': '10.00'}}}
MESSAGE_RESPONSE = {'status': 200, 'body': {'data': {'message': 'Done'}}}

REUSED_KEY_MESSAGE = (
    'This Idempotency-Key was already used for a different request. '
    'Use a new key for each new request.'
)
IN_PROGRESS_MESSAGE = (
    'A request with this Idempotency-Key is still in progress, or did not finish. '
    'Try again shortly; if this persists, check the transaction list before retrying with a new key.'
)

# Each money-moving method, with the arguments it needs and the response it maps.
IDEMPOTENT_CALLS = [
    ('charge_card', ('000010', {'amount': '10.00', 'token': 'tok_abc'}), TXN_RESPONSE),
    ('charge_card_token', ('000010', {'amount': '10.00', 'token': 'tok_abc'}), TXN_RESPONSE),
    ('charge_ach', ('000010', {'amount': '10.00', 'routing_number': '123456789'}), TXN_RESPONSE),
    ('authorize', ('000010', {'amount': '10.00', 'token': 'tok_abc'}), TXN_RESPONSE),
    ('capture', ('000010', '1234567890'), MESSAGE_RESPONSE),
    ('refund', ('000010', {'amount': '5.00', 'transaction_info_id': 100001}), MESSAGE_RESPONSE),
    ('void', ('000010', 'CC', 100001), MESSAGE_RESPONSE),
]


def sent_headers(mock_session: MagicMock, call_index: int = -1) -> dict:
    return mock_session.request.call_args_list[call_index].kwargs.get('headers') or {}


@pytest.mark.parametrize('method, args, response', IDEMPOTENT_CALLS)
def test_generates_an_idempotency_key_when_none_is_given(method, args, response):
    client, mock = fake_client([response])
    getattr(client.transactions, method)(*args)
    key = sent_headers(mock)['Idempotency-Key']
    assert str(uuid.UUID(key)) == key


@pytest.mark.parametrize('method, args, response', IDEMPOTENT_CALLS)
def test_uses_the_callers_idempotency_key_verbatim(method, args, response):
    client, mock = fake_client([response])
    getattr(client.transactions, method)(*args, idempotency_key='order-1001-charge')
    assert sent_headers(mock)['Idempotency-Key'] == 'order-1001-charge'


def test_each_call_gets_its_own_generated_key():
    client, mock = fake_client([TXN_RESPONSE, TXN_RESPONSE])
    client.transactions.charge_card('000010', {'amount': '10.00'})
    client.transactions.charge_card('000010', {'amount': '10.00'})
    assert sent_headers(mock, 0)['Idempotency-Key'] != sent_headers(mock, 1)['Idempotency-Key']


def test_idempotency_key_does_not_change_the_body():
    client, mock = fake_client([TXN_RESPONSE])
    client.transactions.charge_card('000010', {'amount': '10.00'}, idempotency_key='k-1')
    assert mock.request.call_args.kwargs['json'] == {'data': {'sid': '000010', 'amount': '10.00'}}


def test_retry_after_a_timeout_resends_the_same_key():
    mock_session = MagicMock()
    mock_session.request.side_effect = [
        requests.exceptions.ReadTimeout('Read timed out'),
        requests.exceptions.ConnectionError('Connection reset'),
        make_mock_response(200, TXN_RESPONSE['body']),
    ]
    client = Client(Config(token='test-token', session=mock_session, sleep=lambda _: None))

    txn = client.transactions.charge_card('000010', {'amount': '10.00', 'token': 'tok_abc'})

    assert txn.transaction_status == 'Success'
    keys = [call.kwargs['headers']['Idempotency-Key'] for call in mock_session.request.call_args_list]
    assert len(keys) == 3
    assert len(set(keys)) == 1


def test_retry_after_a_server_error_resends_the_same_key():
    client, mock = fake_client([
        {'status': 503, 'body': {'message': 'Service unavailable'}},
        {'status': 502, 'body': {'message': 'Bad gateway'}},
        MESSAGE_RESPONSE,
    ])

    client.transactions.refund('000010', {'amount': '5.00', 'transaction_info_id': 100001}, idempotency_key='refund-77')

    keys = [call.kwargs['headers']['Idempotency-Key'] for call in mock.request.call_args_list]
    assert keys == ['refund-77', 'refund-77', 'refund-77']


def test_non_transaction_calls_send_no_idempotency_key():
    client, mock = fake_client([
        {'status': 200, 'body': {'data': {'token': 'tok_xyz'}}},
        {'status': 200, 'body': {'data': {'transaction_status': 'Success'}}},
        {'status': 200, 'body': {'data': {'id': 1, 'first_name': 'Jane'}}},
    ])
    client.transactions.tokenize_card('000010', {'card_number': '4111111111111111'})
    client.transactions.show('000010', {'transaction_info_id': 100001})
    client.customers.create('000010', {'first_name': 'Jane'})

    for call in mock.request.call_args_list:
        assert 'Idempotency-Key' not in (call.kwargs.get('headers') or {})


def test_multipart_upload_keeps_its_content_type_override():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Uploaded'}}}])
    client.documents.upload('000010', 'Verification', [('statement.pdf', b'%PDF-1.4')])
    assert mock.request.call_args.kwargs['headers'] == {'Content-Type': None}


def test_key_reused_for_a_different_request_raises_idempotency_exception():
    client, _ = fake_client([{'status': 422, 'body': {'data': {'message': REUSED_KEY_MESSAGE}}}])
    with pytest.raises(IdempotencyException) as exc_info:
        client.transactions.charge_card('000010', {'amount': '10.00'}, idempotency_key='k-1')
    assert exc_info.value.status_code == 422
    assert str(exc_info.value) == REUSED_KEY_MESSAGE


def test_key_still_in_progress_raises_idempotency_exception():
    client, _ = fake_client([{'status': 409, 'body': {'data': {'message': IN_PROGRESS_MESSAGE}}}])
    with pytest.raises(IdempotencyException) as exc_info:
        client.transactions.void('000010', 'CC', 100001, idempotency_key='k-1')
    assert exc_info.value.status_code == 409
    assert str(exc_info.value) == IN_PROGRESS_MESSAGE


def test_idempotency_exception_is_an_api_exception():
    client, _ = fake_client([{'status': 409, 'body': {'data': {'message': IN_PROGRESS_MESSAGE}}}])
    with pytest.raises(ApiException):
        client.transactions.capture('000010', '1234567890')


def test_plain_409_still_raises_api_exception():
    client, _ = fake_client([{'status': 409, 'body': {'data': {'message': 'A merchant with this email already exists.'}}}])
    with pytest.raises(ApiException) as exc_info:
        client.merchants.create({'email': 'owner@example.com'})
    assert not isinstance(exc_info.value, IdempotencyException)
    assert exc_info.value.status_code == 409


def test_plain_422_still_raises_validation_exception():
    client, _ = fake_client([{'status': 422, 'body': {'data': {'message': 'Card declined.'}}}])
    with pytest.raises(ValidationException) as exc_info:
        client.transactions.charge_card('000010', {'amount': '10.00'})
    assert str(exc_info.value) == 'Card declined.'
