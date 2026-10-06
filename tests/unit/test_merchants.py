import pytest
from tests.helpers import fake_client, sent_body

MERCHANT_BODY = {
    'sid': '000010',
    'name': 'Test Merchant',
    'mcc': '5411',
    'slug': 'test-merchant',
    'active': True,
    'g_pay': False,
    'a_pay': False,
    'pci_compliance': False,
}


def merchant_response():
    return {'status': 200, 'body': {'data': MERCHANT_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [MERCHANT_BODY], 'meta': {}}}])
    page = client.merchants.list()
    assert len(page) == 1
    assert page.data[0].sid == '000010'


def test_show_maps_merchant():
    client, _ = fake_client([merchant_response()])
    merchant = client.merchants.show('000010')
    assert merchant.name == 'Test Merchant'
    assert merchant.active is True


def test_create_maps_merchant():
    client, _ = fake_client([merchant_response()])
    merchant = client.merchants.create({'name': 'Test Merchant', 'slug': 'test-merchant'})
    assert merchant.sid == '000010'


def test_update_sends_sid_in_data():
    client, mock = fake_client([merchant_response()])
    client.merchants.update('000010', {'name': 'Updated Name'})
    body = sent_body(mock)
    assert body['data']['sid'] == '000010'
    assert body['data']['name'] == 'Updated Name'


def test_get_form_link():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'link': 'https://app.dimepayments.com/onboard/abc'}}}])
    result = client.merchants.get_form_link('000010')
    assert result.link == 'https://app.dimepayments.com/onboard/abc'


def test_application_status_maps_response():
    client, mock = fake_client([{'status': 200, 'body': {'data': {
        'sid': '00069',
        'name': 'Acme Inc',
        'status': 'underwriting',
        'application_status': 'needs_documents',
        'boarded': False,
        'application_submitted_at': '2024-01-15T14:02:11+00:00',
    }}}])
    result = client.merchants.application_status('00069')
    assert result.status == 'underwriting'
    assert result.application_status == 'needs_documents'
    assert result.boarded is False
    assert result.application_submitted_at == '2024-01-15T14:02:11+00:00'
    assert sent_body(mock) == {'data': {'sid': '00069'}}
    assert mock.request.call_args.args[0] == 'GET'
    assert mock.request.call_args.args[1].endswith('merchant/application-status')


def test_application_status_before_onboarding_starts():
    client, _ = fake_client([{'status': 200, 'body': {'data': {
        'sid': '00069',
        'name': 'Acme Inc',
        'status': 'lead',
        'application_status': None,
        'boarded': False,
        'application_submitted_at': None,
    }}}])
    result = client.merchants.application_status('00069')
    assert result.application_status is None
    assert result.application_submitted_at is None
