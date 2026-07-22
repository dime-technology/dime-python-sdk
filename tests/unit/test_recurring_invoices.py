from tests.helpers import fake_client, sent_body

RI_BODY = {
    'id': 3,
    'sid': '000010',
    'customer_uuid': 'cust-uuid-1',
    'frequency': 'Monthly',
    'amount': '99.00',
    'status': 'Active',
    'start_date': '2026-08-01 00:00:00',
}


def ri_response():
    return {'status': 200, 'body': {'data': RI_BODY}}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [RI_BODY], 'meta': {}}}])
    page = client.recurring_invoices.list('000010')
    assert page.data[0].frequency == 'Monthly'
    assert mock.request.call_args.args[1].endswith('recurring-invoices')


def test_show_maps_response():
    client, mock = fake_client([ri_response()])
    ri = client.recurring_invoices.show('000010', 3)
    assert ri.id == 3
    assert ri.amount == '99.00'
    assert sent_body(mock) == {'data': {'sid': '000010', 'recurring_invoice_id': 3}}


def test_create_sends_attributes():
    client, mock = fake_client([ri_response()])
    client.recurring_invoices.create('000010', {
        'customer_uuid': 'cust-uuid-1',
        'frequency': 'Monthly',
        'start_date': '2026-08-01 00:00:00',
        'amount': '99.00',
    })
    body = sent_body(mock)
    assert body['data']['frequency'] == 'Monthly'
    assert mock.request.call_args.args[0] == 'POST'


def test_cancel_sends_recurring_invoice_id():
    client, mock = fake_client([ri_response()])
    client.recurring_invoices.cancel('000010', 3)
    body = sent_body(mock)
    assert body['data']['recurring_invoice_id'] == 3
    assert 'recurring-invoice/cancel' in mock.request.call_args.args[1]
