from tests.helpers import fake_client, sent_body

# Mirrors App\Http\Resources\InvoiceResource.
INVOICE_BODY = {
    'id': 7,
    'token': 'inv-token-7',
    'invoice_number': 'INV-1001',
    'status': 'draft',
    'payment_terms': 'net_15',
    'issue_date': '2026-07-01',
    'due_date': '2026-07-16',
    'is_overdue': False,
    'subtotal': 250.0,
    'total': 250.0,
    'amount_paid': 0.0,
    'balance': 250.0,
    'allow_partial_payment': True,
    'thank_you_note': 'Thanks!',
    'public_url': 'https://pay.example/i/inv-token-7',
    'customer': {'id': 88, 'name': 'Jane Doe', 'email': 'jane@example.com'},
    'items': [
        {
            'id': 1,
            'item_id': 5,
            'name': 'Consulting',
            'description': '2 hours',
            'quantity': 2.0,
            'unit_price': 125.0,
            'amount': 250.0,
        },
    ],
    'payments': [
        {'amount': 100.0, 'paid_at': '2026-07-10T12:00:00+00:00', 'method': 'Visa 4242', 'transaction_id': 4321},
    ],
    'events': [
        {'type': 'created', 'label': 'Created', 'description': 'Invoice created via API', 'created_at': '2026-07-01T09:00:00+00:00'},
    ],
}

# Mirrors the GET /invoice/items payload — Merchant catalog items, not lines.
ITEM_BODY = {'id': 5, 'name': 'Consulting', 'description': 'Professional services', 'price': 125.0}


def invoice_response():
    return {'status': 200, 'body': {'data': INVOICE_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [INVOICE_BODY], 'meta': {}}}])
    page = client.invoices.list('000010')
    assert page.data[0].invoice_number == 'INV-1001'


def test_list_hits_invoices_path():
    client, mock = fake_client([{'status': 200, 'body': {'data': [], 'meta': {}}}])
    client.invoices.list('000010')
    assert mock.request.call_args.args[1].endswith('invoices')


def test_show_maps_the_full_resource():
    client, mock = fake_client([invoice_response()])
    invoice = client.invoices.show('000010', 7)

    assert invoice.id == 7
    assert invoice.payment_terms == 'net_15'
    assert invoice.balance == '250.0'
    assert invoice.public_url == 'https://pay.example/i/inv-token-7'
    assert invoice.allow_partial_payment is True
    assert invoice.is_overdue is False
    assert sent_body(mock) == {'data': {'sid': '000010', 'invoice_id': 7}}


def test_show_maps_the_customer_snapshot():
    client, _ = fake_client([invoice_response()])
    invoice = client.invoices.show('000010', 7)

    assert invoice.customer.id == 88
    assert invoice.customer.name == 'Jane Doe'
    assert invoice.customer.email == 'jane@example.com'


def test_show_maps_line_items_payments_and_events():
    client, _ = fake_client([invoice_response()])
    invoice = client.invoices.show('000010', 7)

    # The API sends these under "items"; reading "line_items" silently yielded [].
    assert len(invoice.items) == 1
    assert invoice.items[0].name == 'Consulting'
    assert invoice.items[0].item_id == 5
    assert invoice.items[0].unit_price == '125.0'

    assert invoice.payments[0].method == 'Visa 4242'
    assert invoice.payments[0].transaction_id == 4321
    assert invoice.events[0].label == 'Created'


def test_create_sends_the_required_fields():
    client, mock = fake_client([invoice_response()])
    client.invoices.create('000010', {
        'customer_uuid': '9f2a6c14-3e8b-4d21-9a77-5c1e0b8f4d33',
        'customer_name': 'Jane Doe',
        'customer_email': 'jane@example.com',
        'payment_terms': 'net_15',
        'lines': [{'item_id': 5, 'name': 'Consulting', 'quantity': 2, 'unit_price': 125}],
    })

    data = sent_body(mock)['data']
    assert data['sid'] == '000010'
    assert data['customer_uuid'] == '9f2a6c14-3e8b-4d21-9a77-5c1e0b8f4d33'
    assert data['payment_terms'] == 'net_15'
    assert data['lines'][0]['item_id'] == 5


def test_update_sends_patch_with_invoice_id():
    client, mock = fake_client([invoice_response()])
    client.invoices.update('000010', 7, {'thank_you_note': 'Updated'})

    assert mock.request.call_args.args[0] == 'PATCH'
    data = sent_body(mock)['data']
    assert data['invoice_id'] == 7
    assert data['thank_you_note'] == 'Updated'


def test_delete_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    assert client.invoices.delete('000010', 7).message == 'Deleted'


def test_send_returns_the_refreshed_invoice():
    client, mock = fake_client([invoice_response()])
    invoice = client.invoices.send('000010', 7)

    assert invoice.id == 7
    assert mock.request.call_args.args[0] == 'POST'
    assert 'invoice/send' in mock.request.call_args.args[1]


def test_mark_sent_returns_invoice():
    client, mock = fake_client([invoice_response()])
    assert client.invoices.mark_sent('000010', 7).id == 7
    assert 'invoice/mark-sent' in mock.request.call_args.args[1]


def test_void_sends_patch():
    client, mock = fake_client([invoice_response()])
    client.invoices.void('000010', 7)
    assert mock.request.call_args.args[0] == 'PATCH'
    assert 'invoice/void' in mock.request.call_args.args[1]


def test_duplicate_returns_invoice():
    client, _ = fake_client([invoice_response()])
    assert client.invoices.duplicate('000010', 7).id == 7


def test_pay_sends_the_required_payment_type():
    client, mock = fake_client([invoice_response()])
    client.invoices.pay('000010', 7, {'payment_type': 'cc', 'token': 'tok_abc', 'amount': 50})

    data = sent_body(mock)['data']
    assert data['invoice_id'] == 7
    assert data['payment_type'] == 'cc'
    assert data['token'] == 'tok_abc'
    assert data['amount'] == 50


def test_pay_supports_ach():
    client, mock = fake_client([invoice_response()])
    client.invoices.pay('000010', 7, {
        'payment_type': 'ach',
        'routing_number': '123456789',
        'account_number': '000123456',
        'account_type': 'Checking',
        'account_name': 'Jane Doe',
    })

    data = sent_body(mock)['data']
    assert data['payment_type'] == 'ach'
    assert data['routing_number'] == '123456789'


def test_get_link_reads_public_url():
    client, _ = fake_client([{
        'status': 200,
        'body': {'data': {'public_url': 'https://pay.example/i/inv-token-7', 'token': 'inv-token-7'}},
    }])
    link = client.invoices.get_link('000010', 7)

    # The API sends public_url; reading "link" always yielded None.
    assert link.public_url == 'https://pay.example/i/inv-token-7'
    assert link.token == 'inv-token-7'


def test_list_items_is_merchant_scoped():
    client, mock = fake_client([{'status': 200, 'body': {'data': [ITEM_BODY]}}])
    items = client.invoices.list_items('000010')

    assert len(items) == 1
    assert items[0].name == 'Consulting'
    assert items[0].price == '125.0'
    # GET /invoice/items takes only sid — no invoice_id.
    assert sent_body(mock) == {'data': {'sid': '000010'}}


def test_create_item_sends_a_name_not_an_item_id():
    client, mock = fake_client([{'status': 200, 'body': {'data': ITEM_BODY}}])
    item = client.invoices.create_item('000010', {
        'name': 'Consulting',
        'description': 'Professional services',
        'price': 125,
        'tax_deductible': False,
    })

    data = sent_body(mock)['data']
    assert data['name'] == 'Consulting'
    assert 'invoice_id' not in data
    assert item.id == 5
    assert 'invoice/item/create' in mock.request.call_args.args[1]


def test_add_line_item_returns_the_refreshed_invoice():
    client, mock = fake_client([invoice_response()])
    invoice = client.invoices.add_line_item('000010', 7, {
        'item_id': 5,
        'name': 'Consulting',
        'quantity': 2,
        'unit_price': 125,
    })

    data = sent_body(mock)['data']
    assert data['invoice_id'] == 7
    assert data['item_id'] == 5
    assert invoice.total == '250.0'
    assert 'invoice/line-item/add' in mock.request.call_args.args[1]


def test_update_line_item_sends_both_ids():
    client, mock = fake_client([invoice_response()])
    client.invoices.update_line_item('000010', 7, 1, {'quantity': 3})

    assert mock.request.call_args.args[0] == 'PATCH'
    data = sent_body(mock)['data']
    # invoice_id is required by the endpoint; omitting it 400'd every call.
    assert data['invoice_id'] == 7
    assert data['line_item_id'] == 1
    assert data['quantity'] == 3


def test_delete_line_item_sends_both_ids_and_returns_invoice():
    client, mock = fake_client([invoice_response()])
    invoice = client.invoices.delete_line_item('000010', 7, 1)

    data = sent_body(mock)['data']
    assert data['invoice_id'] == 7
    assert data['line_item_id'] == 1
    assert invoice.id == 7
