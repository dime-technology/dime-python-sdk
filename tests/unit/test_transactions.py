import pytest
from tests.helpers import fake_client, sent_body

TXN_BODY = {
    'transaction_type': 'CC',
    'transaction_status': 'Success',
    'amount': '49.99',
    'pending': False,
    'billing_address': {'addr1': '123 Main St', 'city': 'Atlanta', 'state': 'GA', 'zip': '30301'},
    'shippingAddress': {},
    'transaction_info_id': '100001',
}


def txn_response():
    return {'status': 200, 'body': {'data': TXN_BODY}}


def test_charge_card_maps_response():
    client, _ = fake_client([txn_response()])
    txn = client.transactions.charge_card('000010', {'amount': '49.99', 'token': 'tok_abc'})
    assert txn.transaction_status == 'Success'
    assert txn.amount == '49.99'


def test_charge_card_sends_correct_envelope():
    client, mock = fake_client([txn_response()])
    client.transactions.charge_card('000010', {'amount': '49.99', 'token': 'tok_abc'})
    body = sent_body(mock)
    assert body == {'data': {'sid': '000010', 'amount': '49.99', 'token': 'tok_abc'}}


def test_charge_card_uses_post():
    client, mock = fake_client([txn_response()])
    client.transactions.charge_card('000010', {'amount': '10.00'})
    assert mock.request.call_args.args[0] == 'POST'


def test_charge_ach_maps_response():
    client, _ = fake_client([txn_response()])
    txn = client.transactions.charge_ach('000010', {
        'routing_number': '123456789',
        'account_number': '9876543210',
        'account_type': 'Checking',
        'account_name': 'John Doe',
        'amount': '75.00',
    })
    assert txn.transaction_type == 'CC'


def test_tokenize_card_returns_token():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'token': 'tok_xyz'}}}])
    result = client.transactions.tokenize_card('000010', {'cardholder_name': 'Jane', 'card_number': '4111111111111111', 'expiration_date': '01/2027'})
    assert result.token == 'tok_xyz'


def test_refund_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Refund processed'}}}])
    result = client.transactions.refund('000010', {'amount': '25.00', 'transaction_info_id': 100001})
    assert result.message == 'Refund processed'


def test_void_sends_transaction_id():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Voided'}}}])
    client.transactions.void('000010', 'CC', 100001)
    body = sent_body(mock)
    assert body['data']['transaction_type'] == 'CC'
    assert body['data']['transaction_id'] == 100001


def test_show_maps_billing_address():
    client, _ = fake_client([txn_response()])
    txn = client.transactions.show('000010', {'transaction_info_id': 100001})
    assert txn.billing_address.addr1 == '123 Main St'


def test_list_returns_cursor_page():
    client, _ = fake_client([{
        'status': 200,
        'body': {'data': [TXN_BODY], 'meta': {'next_cursor': None, 'prev_cursor': None, 'per_page': 500}},
    }])
    page = client.transactions.list('000010')
    assert len(page) == 1
    assert page.data[0].amount == '49.99'


def test_shipping_address_camel_case_key():
    client, _ = fake_client([{'status': 200, 'body': {'data': {
        **TXN_BODY,
        'shippingAddress': {'addr1': '456 Oak Ave'},
    }}}])
    txn = client.transactions.show('000010', {'transaction_info_id': 1})
    assert txn.shipping_address.addr1 == '456 Oak Ave'


def test_authorize_sends_envelope_and_maps_transaction():
    client, mock = fake_client([{'status': 200, 'body': {'data': TXN_BODY | {
        'transaction_status': 'Pending',
        'transaction_number': '1234567890',
        'pending': True,
    }}}])
    txn = client.transactions.authorize('000010', {'amount': '100.50', 'token': 'tok_abc'})
    assert txn.transaction_number == '1234567890'
    assert txn.pending is True
    assert sent_body(mock) == {'data': {'sid': '000010', 'amount': '100.50', 'token': 'tok_abc'}}
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('transaction/authorize')


def test_capture_full_amount_omits_amount():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Transaction captured successfully.'}}}])
    result = client.transactions.capture('000010', '1234567890')
    assert result.message == 'Transaction captured successfully.'
    assert sent_body(mock) == {'data': {'sid': '000010', 'transaction_id': '1234567890'}}
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('transaction/capture')


def test_capture_partial_amount():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Transaction captured successfully.'}}}])
    client.transactions.capture('000010', 1234567890, '50.00')
    assert sent_body(mock) == {'data': {'sid': '000010', 'transaction_id': 1234567890, 'amount': '50.00'}}


def test_capture_says_what_it_took():
    from dime_payments.data_objects import CaptureResult, MessageResult

    client, _ = fake_client([{'status': 200, 'body': {'data': {
        'message': 'Transaction captured successfully.',
        'transaction_id': '1234567890',
        'authorized_amount': '120.00',
        'captured_amount': '50.00',
        'status': 'captured',
        'captured_at': '2026-10-13T15:02:11-04:00',
    }}}])
    result = client.transactions.capture('000010', '1234567890', '50.00')
    assert isinstance(result, CaptureResult)
    assert isinstance(result, MessageResult)
    assert result.message == 'Transaction captured successfully.'
    assert result.transaction_id == '1234567890'
    assert result.authorized_amount == '120.00'
    assert result.captured_amount == '50.00'
    assert result.status == 'captured'
    assert result.captured_at == '2026-10-13T15:02:11-04:00'


def test_capture_fields_are_none_against_an_api_that_only_sends_a_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Transaction captured successfully.'}}}])
    result = client.transactions.capture('000010', '1234567890')
    assert result.message == 'Transaction captured successfully.'
    assert result.captured_amount is None
    assert result.status is None


@pytest.mark.parametrize(('code', 'message'), [
    ('not_found', 'No transaction found.'),
    ('already_captured', 'Transaction is not an open authorization.'),
    ('voided', 'Transaction is not an open authorization.'),
    ('refunded', 'Transaction is not an open authorization.'),
    ('authorization_declined', 'Transaction is not an open authorization.'),
    ('not_an_authorization', 'Transaction is not an open authorization.'),
    ('amount_exceeds_authorization', 'Amount cannot be greater than the authorized amount'),
    ('some_future_code', 'Something new.'),
])
def test_refused_capture_raises_capture_exception_with_its_code(code, message):
    from dime_payments import ApiException, CaptureException, ValidationException

    client, _ = fake_client([{'status': 400, 'body': {'data': {'message': message, 'code': code}}}])
    with pytest.raises(CaptureException) as exc_info:
        client.transactions.capture('000010', '1234567890')
    error = exc_info.value
    assert isinstance(error, ApiException)
    assert isinstance(error, ValidationException)  # what a refusal raised before 1.6.0
    assert error.error_code == code
    assert error.get_error_code() == code
    assert str(error) == message
    assert error.reason is None
    assert error.status_code == 400


def test_declined_capture_carries_the_reason():
    from dime_payments import CaptureException

    client, _ = fake_client([{'status': 400, 'body': {'data': {
        'message': 'Error processing capture',
        'code': 'processor_declined',
        'reason': 'Transaction rejected because the authorization has expired.',
    }}}])
    with pytest.raises(CaptureException) as exc_info:
        client.transactions.capture('000010', '1234567890', '50.00')
    assert exc_info.value.error_code == 'processor_declined'
    assert exc_info.value.reason == 'Transaction rejected because the authorization has expired.'
    assert exc_info.value.get_reason() == 'Transaction rejected because the authorization has expired.'


def test_capture_validation_error_stays_a_validation_exception():
    from dime_payments import CaptureException, ValidationException

    client, _ = fake_client([{'status': 400, 'body': {
        'errors': {'data.transaction_id': ['The data.transaction_id field is required.']},
    }}])
    with pytest.raises(ValidationException) as exc_info:
        client.transactions.capture('000010', '')
    assert not isinstance(exc_info.value, CaptureException)
    assert exc_info.value.first_error() == 'The data.transaction_id field is required.'


def test_idempotency_refusal_on_capture_stays_an_idempotency_exception():
    from dime_payments import CaptureException, IdempotencyException

    client, _ = fake_client([{'status': 422, 'body': {'data': {
        'message': 'This Idempotency-Key was already used for a different request. Use a new key for each new request.',
    }}}])
    with pytest.raises(IdempotencyException) as exc_info:
        client.transactions.capture('000010', '1234567890', idempotency_key='k-1')
    assert not isinstance(exc_info.value, CaptureException)


def test_capture_refusal_surfaces_api_message():
    from dime_payments import CaptureException, ValidationException

    # An API that predates data.code: the refusal keeps its old exception type.
    client, _ = fake_client([{'status': 400, 'body': {'data': {'message': 'Transaction is not an open authorization.'}}}])
    with pytest.raises(ValidationException) as exc_info:
        client.transactions.capture('000010', '1234567890')
    assert str(exc_info.value) == 'Transaction is not an open authorization.'
    assert not isinstance(exc_info.value, CaptureException)
