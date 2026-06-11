import pytest
from tests.helpers import fake_client, sent_body

RP_BODY = {
    'id': 5,
    'name': 'Monthly donation',
    'amount': '25.00',
    'start_date': '2026-07-01 00:00:00',
    'recurrence_schedule': 'Monthly',
    'status': 'Active',
    'payment_method': {'id': 42, 'type': 'cc'},
    'shipping_address': {},
}


def rp_response():
    return {'status': 200, 'body': {'data': RP_BODY}}


def test_create_maps_response():
    client, _ = fake_client([rp_response()])
    rp = client.recurring_payments.create('000010', {
        'name': 'Monthly donation',
        'amount': '25.00',
        'start_date': '2026-07-01 00:00:00',
        'recurrence_schedule': 'Monthly',
        'payment_method': 42,
        'customer_uuid': 'cust-uuid-1',
    })
    assert rp.id == 5
    assert rp.amount == '25.00'
    assert rp.payment_method.id == 42


def test_pause_sends_pause_until_date():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.pause('000010', 5, '2026-09-01 00:00:00')
    body = sent_body(mock)
    assert body == {'data': {'sid': '000010', 'recurring_payment_id': 5, 'pause_until_date': '2026-09-01 00:00:00'}}


def test_pause_without_date_omits_pause_until_date():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.pause('000010', 5)
    body = sent_body(mock)
    assert 'pause_until_date' not in body.get('data', {})


def test_cancel_sends_patch_to_correct_path():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.cancel('000010', 5)
    assert 'recurring-payment/cancel' in mock.request.call_args.args[1]


def test_activate_sends_patch():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.activate('000010', 5)
    assert mock.request.call_args.args[0] == 'PATCH'


def test_delete_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    result = client.recurring_payments.delete('000010', 5)
    assert result.message == 'Deleted'


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [RP_BODY], 'meta': {}}}])
    page = client.recurring_payments.list('000010')
    assert page.data[0].name == 'Monthly donation'


def test_edit_sends_recurring_payment_id():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.edit('000010', 5, {'amount': '30.00'})
    body = sent_body(mock)
    assert body['data']['recurring_payment_id'] == 5
    assert body['data']['amount'] == '30.00'
