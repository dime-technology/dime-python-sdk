from tests.helpers import fake_client, sent_body

SUB_BODY = {
    'id': 1,
    'subscription_plan_id': 2,
    'plan_name': 'asdsadasd',
    'amount': '10.00',
    'recurrence_schedule': 'Monthly',
    'start_date': '2026-07-22T04:00:00.000000Z',
    'end_date': None,
    'last_run_date': '2026-07-22T04:00:00.000000Z',
    'last_run_status': 'Success',
    'last_run_failed_count': 0,
    'next_run_date': None,
    'status': 'Cancelled',
    'paused_until_date': None,
    'cancelled_at': '2026-07-22T20:31:28.000000Z',
    'cancelled_by': 'Marcus Whitesides APIClient',
    'customer_uuid': 'e18537dc-bd45-41d2-be2e-fe6e703c4bfa',
    'error': None,
    'payment_method': {'id': 5600, 'type': 'cc', 'last_four': '1111', 'expiration': '12/2030'},
    'items': [
        {'name': 'General', 'description': None, 'quantity': 1, 'unit_price': 10, 'amount': 10},
    ],
}


def sub_response():
    return {'status': 200, 'body': {'data': SUB_BODY}}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [SUB_BODY], 'meta': {}}}])
    page = client.subscriptions.list('000010')
    assert page.data[0].plan_name == 'asdsadasd'
    assert page.data[0].last_run_failed_count == 0
    assert page.data[0].payment_method.last_four == '1111'
    assert mock.request.call_args.args[1].endswith('subscription/list')


def test_list_sends_filters_envelope():
    client, mock = fake_client([{'status': 200, 'body': {'data': [SUB_BODY], 'meta': {}}}])
    client.subscriptions.list('000010', {
        'status': 'Active',
        'customer_uuid': 'cust-uuid-1',
    })
    assert sent_body(mock) == {
        'data': {'sid': '000010'},
        'filters': {'status': 'Active', 'customer_uuid': 'cust-uuid-1'},
    }


def test_show_maps_response():
    client, mock = fake_client([sub_response()])
    sub = client.subscriptions.show('000010', 1)
    assert sub.id == 1
    assert sub.amount == '10.00'
    assert sub.items[0].amount == '10'
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 1}}
    assert mock.request.call_args.args[0] == 'GET'


def test_pause_sends_pause_until_date():
    client, mock = fake_client([sub_response()])
    client.subscriptions.pause('000010', 42, '2026-09-01')
    body = sent_body(mock)
    assert body['data'] == {
        'sid': '000010',
        'subscription_id': 42,
        'pause_until_date': '2026-09-01',
    }
    assert mock.request.call_args.args[0] == 'PATCH'
    assert mock.request.call_args.args[1].endswith('subscription/pause')


def test_pause_omits_date_when_not_given():
    client, mock = fake_client([sub_response()])
    client.subscriptions.pause('000010', 42)
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 42}}


def test_resume_and_cancel_use_patch():
    for method, path in (('resume', 'resume'), ('cancel', 'cancel')):
        client, mock = fake_client([sub_response()])
        sub = getattr(client.subscriptions, method)('000010', 42)
        assert sub.id == 1
        assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 42}}
        assert mock.request.call_args.args[0] == 'PATCH'
        assert mock.request.call_args.args[1].endswith(f'subscription/{path}')
