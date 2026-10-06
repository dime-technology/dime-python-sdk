import pytest
from dime_payments import NotFoundException
from tests.helpers import fake_client, sent_body

CHARGEBACK_BODY = {
    'transaction_info_id': '8675309',
    'parent_transaction_info_id': '8675000',
    'gateway_transaction_id': '412',
    'transaction_number': '412',
    'invoice_number': 'INV-1',
    'chargeback_date': '2026-04-02T00:00:00+00:00',
    'merchant_chargeback_date': '2026-04-02T00:00:00+00:00',
    'transaction_amount': 120.5,
    'chargeback_amount': 100,
    'card_brand': 'Visa',
    'cc_last_four': '1111',
    'payee_name': 'Jane Doe',
    'days_to_represent': 10,
    'representment_date': '2026-04-12T00:00:00+00:00',
    'merchant_representment_date': '2026-04-10T00:00:00+00:00',
    'representment_status': 'New',
    'result': None,
    'chargeback_code': '4834',
    'chargeback_response_code': 'Duplicate Processing',
    'resolved': False,
}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [CHARGEBACK_BODY], 'meta': {'next_cursor': None}}}])
    page = client.chargebacks.list('000010')
    assert page.data[0].transaction_info_id == '8675309'
    assert page.data[0].chargeback_amount == '100'
    assert page.data[0].days_to_represent == 10
    assert page.data[0].resolved is False
    assert mock.request.call_args.args[0] == 'GET'
    assert mock.request.call_args.args[1].endswith('chargeback/list')


def test_list_sends_filters():
    client, mock = fake_client([{'status': 200, 'body': {'data': [CHARGEBACK_BODY], 'meta': {}}}])
    client.chargebacks.list('000010', {
        'start_date': '2026-04-01 00:00:00',
        'end_date': '2026-04-30 23:59:59',
        'representment_status': 'New',
    })
    assert sent_body(mock) == {
        'data': {'sid': '000010'},
        'filters': {
            'start_date': '2026-04-01 00:00:00',
            'end_date': '2026-04-30 23:59:59',
            'representment_status': 'New',
        },
    }


def test_list_next_page_resends_body_with_cursor():
    client, mock = fake_client([
        {'status': 200, 'body': {'data': [CHARGEBACK_BODY], 'meta': {'next_cursor': 'abc'}}},
        {'status': 200, 'body': {'data': [CHARGEBACK_BODY], 'meta': {}}},
    ])
    client.chargebacks.list('000010').next()
    assert sent_body(mock) == {'data': {'sid': '000010'}}
    assert mock.request.call_args.kwargs['params'] == {'cursor': 'abc'}


def test_list_raises_not_found_when_empty():
    client, _ = fake_client([{'status': 404, 'body': {'data': {'message': 'No chargebacks found'}}}])
    with pytest.raises(NotFoundException) as exc_info:
        client.chargebacks.list('000010')
    assert str(exc_info.value) == 'No chargebacks found'


def test_show_sends_transaction_info_id():
    client, mock = fake_client([{'status': 200, 'body': {'data': CHARGEBACK_BODY}}])
    chargeback = client.chargebacks.show('000010', '8675309')
    assert chargeback.chargeback_response_code == 'Duplicate Processing'
    assert sent_body(mock) == {'data': {'sid': '000010', 'transaction_info_id': '8675309'}}
    assert mock.request.call_args.args[1].endswith('chargeback/show')
