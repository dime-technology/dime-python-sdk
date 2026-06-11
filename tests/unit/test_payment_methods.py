import pytest
from tests.helpers import fake_client, sent_body

PM_BODY = {
    'id': 42,
    'type': 'cc',
    'cc_name_on_card': 'Jane Doe',
    'cc_last_four': '1111',
    'cc_expiration_date': '01/2027',
    'cc_brand': 'Visa',
    'enabled': True,
    'default': True,
}


def pm_response():
    return {'status': 200, 'body': {'data': PM_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [PM_BODY], 'meta': {}}}])
    page = client.payment_methods.list('000010', {'uuid': 'cust-1'})
    assert len(page) == 1
    assert page.data[0].id == 42


def test_show_maps_payment_method():
    client, _ = fake_client([pm_response()])
    pm = client.payment_methods.show('000010', 42, {'uuid': 'cust-1'})
    assert pm.cc_name_on_card == 'Jane Doe'
    assert pm.is_default is True


def test_show_sends_payment_method_id_in_data():
    client, mock = fake_client([pm_response()])
    client.payment_methods.show('000010', 42, {'uuid': 'cust-1'})
    body = sent_body(mock)
    assert body['data']['payment_method_id'] == 42
    assert body['filters']['uuid'] == 'cust-1'


def test_create_maps_payment_method():
    client, _ = fake_client([pm_response()])
    pm = client.payment_methods.create('000010', {
        'uuid': 'cust-1',
        'type': 'cc',
        'cc_name_on_card': 'Jane Doe',
        'cc_number': '4111111111111111',
        'cc_expiration_date': '01/2027',
    })
    assert pm.id == 42
    assert pm.cc_brand == 'Visa'


def test_delete_uses_post_with_uuid():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    client.payment_methods.delete('000010', 42, 'cust-1')
    assert mock.request.call_args.args[0] == 'POST'
    body = sent_body(mock)
    assert body['data']['payment_method_id'] == 42
    assert body['data']['uuid'] == 'cust-1'
