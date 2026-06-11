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
