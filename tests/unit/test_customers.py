import pytest
from tests.helpers import fake_client, sent_body

CUSTOMER_BODY = {
    'uuid': 'cust-uuid-1',
    'first_name': 'Jane',
    'last_name': 'Doe',
    'email': 'jane@example.com',
    'phone': '5555555555',
}


def customer_response():
    return {'status': 200, 'body': {'data': CUSTOMER_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{
        'status': 200,
        'body': {'data': [CUSTOMER_BODY], 'meta': {}},
    }])
    page = client.customers.list('000010')
    assert len(page) == 1
    assert page.data[0].uuid == 'cust-uuid-1'


def test_show_maps_customer():
    client, _ = fake_client([customer_response()])
    customer = client.customers.show('000010', {'uuid': 'cust-uuid-1'})
    assert customer.first_name == 'Jane'
    assert customer.last_name == 'Doe'


def test_show_sends_filters_envelope():
    client, mock = fake_client([customer_response()])
    client.customers.show('000010', {'uuid': 'cust-uuid-1'})
    body = sent_body(mock)
    assert body.get('data', {}).get('sid') == '000010'
    assert body.get('filters', {}).get('uuid') == 'cust-uuid-1'


def test_create_maps_customer():
    client, _ = fake_client([customer_response()])
    customer = client.customers.create('000010', {'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@example.com'})
    assert customer.uuid == 'cust-uuid-1'


def test_create_sends_data_envelope():
    client, mock = fake_client([customer_response()])
    client.customers.create('000010', {'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@example.com'})
    body = sent_body(mock)
    assert body['data']['sid'] == '000010'
    assert body['data']['first_name'] == 'Jane'


def test_update_sends_data_and_filters():
    client, mock = fake_client([customer_response()])
    client.customers.update('000010', {'uuid': 'cust-uuid-1'}, {'first_name': 'Jane'})
    body = sent_body(mock)
    assert body['data']['sid'] == '000010'
    assert body['data']['first_name'] == 'Jane'
    assert body['filters']['uuid'] == 'cust-uuid-1'


def test_delete_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    result = client.customers.delete('000010', {'uuid': 'cust-uuid-1'})
    assert result.message == 'Deleted'
