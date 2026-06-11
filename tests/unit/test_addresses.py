import pytest
from tests.helpers import fake_client, sent_body

ADDRESS_BODY = {
    'id': 7,
    'recipient': 'Jane Doe',
    'line_one': '123 Main St',
    'city': 'Atlanta',
    'state': 'GA',
    'zip': '30301',
}

ADDRESS_SHOW_BODY = {**ADDRESS_BODY, 'address_id': 7}


def address_response():
    return {'status': 200, 'body': {'data': ADDRESS_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [ADDRESS_BODY], 'meta': {}}}])
    page = client.addresses.list('000010', 'cust-uuid-1')
    assert len(page) == 1
    assert page.data[0].recipient == 'Jane Doe'


def test_show_reads_address_id_key():
    client, _ = fake_client([{'status': 200, 'body': {'data': ADDRESS_SHOW_BODY}}])
    address = client.addresses.show('000010', 'cust-uuid-1', 7)
    assert address.id == 7


def test_create_maps_address():
    client, _ = fake_client([address_response()])
    address = client.addresses.create('000010', 'cust-uuid-1', {
        'recipient': 'Jane Doe',
        'line_one': '123 Main St',
        'city': 'Atlanta',
        'state': 'GA',
        'zip': '30301',
    })
    assert address.line_one == '123 Main St'


def test_create_sends_sid_and_uuid():
    client, mock = fake_client([address_response()])
    client.addresses.create('000010', 'cust-uuid-1', {'recipient': 'Jane Doe', 'line_one': '123 Main St', 'city': 'Atlanta', 'state': 'GA', 'zip': '30301'})
    body = sent_body(mock)
    assert body['data']['sid'] == '000010'
    assert body['data']['uuid'] == 'cust-uuid-1'


def test_update_sends_address_id():
    client, mock = fake_client([address_response()])
    client.addresses.update('000010', 'cust-uuid-1', 7, {'recipient': 'John Doe'})
    body = sent_body(mock)
    assert body['data']['address_id'] == 7


def test_delete_uses_post():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    client.addresses.delete('000010', 'cust-uuid-1', 7)
    assert mock.request.call_args.args[0] == 'POST'
    body = sent_body(mock)
    assert body['data']['address_id'] == 7
