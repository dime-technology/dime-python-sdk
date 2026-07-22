from tests.helpers import fake_client, sent_body

INVOICE_BODY = {
    'id': 7,
    'sid': '000010',
    'invoice_number': 'INV-1001',
    'customer_uuid': 'cust-uuid-1',
    'status': 'Draft',
    'due_date': '2026-08-01 00:00:00',
    'total': '150.00',
    'amount_due': '150.00',
    'line_items': [
        {'id': 1, 'invoice_id': 7, 'description': 'Consulting', 'quantity': '2', 'amount': '75.00', 'total': '150.00'},
    ],
}

LINE_ITEM_BODY = {
    'id': 1,
    'invoice_id': 7,
    'description': 'Consulting',
    'quantity': '2',
    'amount': '75.00',
    'total': '150.00',
}


def invoice_response():
    return {'status': 200, 'body': {'data': INVOICE_BODY}}


def line_item_response():
    return {'status': 200, 'body': {'data': LINE_ITEM_BODY}}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [INVOICE_BODY], 'meta': {}}}])
    page = client.invoices.list('000010')
    assert page.data[0].invoice_number == 'INV-1001'


def test_list_hits_invoices_path():
    client, mock = fake_client([{'status': 200, 'body': {'data': [], 'meta': {}}}])
    client.invoices.list('000010')
    assert mock.request.call_args.args[1].endswith('invoices')


def test_show_maps_response_and_line_items():
    client, mock = fake_client([invoice_response()])
    invoice = client.invoices.show('000010', 7)
    assert invoice.id == 7
    assert invoice.total == '150.00'
    assert invoice.line_items[0].description == 'Consulting'
    assert sent_body(mock) == {'data': {'sid': '000010', 'invoice_id': 7}}


def test_create_sends_attributes():
    client, mock = fake_client([invoice_response()])
    client.invoices.create('000010', {
        'customer_uuid': 'cust-uuid-1',
        'due_date': '2026-08-01 00:00:00',
        'invoice_number': 'INV-1001',
    })
    body = sent_body(mock)
    assert body['data']['customer_uuid'] == 'cust-uuid-1'
    assert body['data']['sid'] == '000010'


def test_update_sends_patch_with_invoice_id():
    client, mock = fake_client([invoice_response()])
    client.invoices.update('000010', 7, {'notes': 'Updated'})
    assert mock.request.call_args.args[0] == 'PATCH'
    body = sent_body(mock)
    assert body['data']['invoice_id'] == 7
    assert body['data']['notes'] == 'Updated'


def test_delete_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    result = client.invoices.delete('000010', 7)
    assert result.message == 'Deleted'


def test_send_posts_to_send_path():
    client, mock = fake_client([{'status': 200, 'body': {'data': {'message': 'Sent'}}}])
    result = client.invoices.send('000010', 7)
    assert result.message == 'Sent'
    assert mock.request.call_args.args[0] == 'POST'
    assert 'invoice/send' in mock.request.call_args.args[1]


def test_void_sends_patch():
    client, mock = fake_client([invoice_response()])
    client.invoices.void('000010', 7)
    assert mock.request.call_args.args[0] == 'PATCH'
    assert 'invoice/void' in mock.request.call_args.args[1]


def test_pay_includes_amount_when_given():
    client, mock = fake_client([invoice_response()])
    client.invoices.pay('000010', 7, '50.00')
    assert sent_body(mock)['data']['amount'] == '50.00'


def test_pay_omits_amount_when_absent():
    client, mock = fake_client([invoice_response()])
    client.invoices.pay('000010', 7)
    assert 'amount' not in sent_body(mock).get('data', {})


def test_duplicate_returns_invoice():
    client, _ = fake_client([invoice_response()])
    invoice = client.invoices.duplicate('000010', 7)
    assert invoice.id == 7


def test_get_link_returns_form_link():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'link': 'https://pay.example/inv/7'}}}])
    link = client.invoices.get_link('000010', 7)
    assert link.link == 'https://pay.example/inv/7'


def test_list_items_returns_list():
    client, _ = fake_client([{'status': 200, 'body': {'data': [LINE_ITEM_BODY]}}])
    items = client.invoices.list_items('000010', 7)
    assert len(items) == 1
    assert items[0].amount == '75.00'


def test_add_line_item_posts_attributes():
    client, mock = fake_client([line_item_response()])
    client.invoices.add_line_item('000010', 7, {
        'description': 'Consulting',
        'quantity': '2',
        'amount': '75.00',
    })
    body = sent_body(mock)
    assert body['data']['invoice_id'] == 7
    assert body['data']['description'] == 'Consulting'
    assert 'invoice/line-item/add' in mock.request.call_args.args[1]


def test_update_line_item_sends_line_item_id():
    client, mock = fake_client([line_item_response()])
    client.invoices.update_line_item('000010', 1, {'quantity': '3'})
    assert mock.request.call_args.args[0] == 'PATCH'
    assert sent_body(mock)['data']['line_item_id'] == 1


def test_delete_line_item_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Removed'}}}])
    result = client.invoices.delete_line_item('000010', 1)
    assert result.message == 'Removed'


def test_create_item_sends_item_id():
    client, mock = fake_client([line_item_response()])
    client.invoices.create_item('000010', 7, 99)
    body = sent_body(mock)
    assert body['data']['item_id'] == 99
    assert body['data']['invoice_id'] == 7
    assert 'invoice/item/create' in mock.request.call_args.args[1]
