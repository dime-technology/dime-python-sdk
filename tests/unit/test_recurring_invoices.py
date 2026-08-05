from tests.helpers import fake_client, sent_body

# Mirrors App\Http\Resources\RecurringInvoiceResource.
RI_BODY = {
    'id': 3,
    'status': 'active',
    'recurrence_schedule': 'Monthly',
    'payment_terms': 'net_30',
    'start_date': '2026-09-01',
    'end_date': None,
    'next_run_date': '2026-09-01',
    'last_run_date': None,
    'thank_you_note': 'Thanks!',
    'customer': {'id': 88, 'name': 'Jane Doe', 'email': 'jane@example.com'},
    'items': [
        {'id': 1, 'item_id': 5, 'name': 'Retainer', 'description': None, 'quantity': 1.0, 'unit_price': 500.0, 'amount': 500.0},
    ],
    'upcoming_run_dates': ['2026-09-01', '2026-10-01', '2026-11-01'],
    'invoices': [
        {'id': 41, 'invoice_number': 'INV-0041', 'status': 'paid', 'total': 500.0, 'issue_date': '2026-08-01'},
    ],
}


def ri_response():
    return {'status': 200, 'body': {'data': RI_BODY}}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [RI_BODY], 'meta': {}}}])
    page = client.recurring_invoices.list('000010')

    assert page.data[0].recurrence_schedule == 'Monthly'
    assert mock.request.call_args.args[1].endswith('recurring-invoices')


def test_show_maps_the_full_resource():
    client, mock = fake_client([ri_response()])
    ri = client.recurring_invoices.show('000010', 3)

    assert ri.id == 3
    assert ri.status == 'active'
    assert ri.recurrence_schedule == 'Monthly'
    assert ri.payment_terms == 'net_30'
    assert ri.next_run_date == '2026-09-01'
    assert sent_body(mock) == {'data': {'sid': '000010', 'recurring_invoice_id': 3}}


def test_show_maps_customer_items_and_schedule():
    client, _ = fake_client([ri_response()])
    ri = client.recurring_invoices.show('000010', 3)

    assert ri.customer.name == 'Jane Doe'
    assert ri.items[0].name == 'Retainer'
    assert ri.items[0].unit_price == '500.0'
    assert ri.upcoming_run_dates == ['2026-09-01', '2026-10-01', '2026-11-01']
    assert ri.invoices[0].invoice_number == 'INV-0041'


def test_create_sends_the_api_field_names():
    client, mock = fake_client([ri_response()])
    client.recurring_invoices.create('000010', {
        'customer_uuid': '9f2a6c14-3e8b-4d21-9a77-5c1e0b8f4d33',
        'payment_terms': 'net_30',
        'recurring_frequency': 'Monthly',
        'recurring_start_date': '2026-09-01',
        'lines': [{'item_id': 5, 'name': 'Retainer', 'quantity': 1, 'unit_price': 500}],
    })

    data = sent_body(mock)['data']
    # The endpoint wants recurring_frequency / recurring_start_date / lines.
    assert data['recurring_frequency'] == 'Monthly'
    assert data['recurring_start_date'] == '2026-09-01'
    assert data['lines'][0]['item_id'] == 5
    assert mock.request.call_args.args[0] == 'POST'


def test_cancel_sends_recurring_invoice_id():
    client, mock = fake_client([ri_response()])
    client.recurring_invoices.cancel('000010', 3)

    assert sent_body(mock)['data']['recurring_invoice_id'] == 3
    assert 'recurring-invoice/cancel' in mock.request.call_args.args[1]
