import pytest
from tests.helpers import fake_client, sent_body

SUB_BODY = {
    'id': 1,
    'subscription_plan_id': 2,
    'plan_name': 'Monthly Membership',
    'amount': '10.00',
    'recurrence_schedule': 'Monthly',
    'start_date': '2026-07-22T04:00:00.000000Z',
    'end_date': None,
    'last_run_date': '2026-07-22T04:00:00.000000Z',
    'last_run_status': 'Success',
    'last_run_failed_count': 0,
    'next_run_date': '2026-08-22T04:00:00.000000Z',
    'status': 'Active',
    'paused_until_date': None,
    'cancelled_at': None,
    'cancelled_by': None,
    'customer_uuid': 'e18537dc-bd45-41d2-be2e-fe6e703c4bfa',
    'error': None,
    'payment_method': {'id': 5600, 'type': 'cc', 'last_four': '1111', 'expiration': '12/2030'},
    'items': [
        {'name': 'General', 'description': None, 'quantity': 1, 'unit_price': 10, 'amount': 10},
    ],
}


def sub_response(**overrides):
    return {'status': 200, 'body': {'data': SUB_BODY | overrides}}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [SUB_BODY], 'meta': {}}}])
    page = client.subscriptions.list('000010')
    assert page.data[0].plan_name == 'Monthly Membership'
    assert page.data[0].last_run_failed_count == 0
    assert page.data[0].payment_method.last_four == '1111'
    assert mock.request.call_args.args[1].endswith('subscription/list')


def test_list_sends_filters():
    client, mock = fake_client([{'status': 200, 'body': {'data': [SUB_BODY], 'meta': {}}}])
    client.subscriptions.list('000010', {'status': 'Active', 'customer_uuid': 'cust-uuid-1'})
    assert sent_body(mock) == {
        'data': {'sid': '000010'},
        'filters': {'status': 'Active', 'customer_uuid': 'cust-uuid-1'},
    }


def test_show_maps_items_and_payment_method():
    client, mock = fake_client([sub_response()])
    sub = client.subscriptions.show('000010', 1)
    assert sub.id == 1
    assert sub.subscription_plan_id == 2
    assert sub.items[0].amount == '10'
    assert sub.payment_method.id == 5600
    assert sub.payment_method.expiration == '12/2030'
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 1}}
    assert mock.request.call_args.args[0] == 'GET'


def test_ach_payment_method_maps_bank_fields():
    client, _ = fake_client([sub_response(payment_method={
        'id': 7, 'type': 'ach', 'bank_name': 'First Bank', 'account_type': 'Checking',
    })])
    sub = client.subscriptions.show('000010', 1)
    assert sub.payment_method.bank_name == 'First Bank'
    assert sub.payment_method.account_type == 'Checking'
    assert sub.payment_method.last_four is None


def test_missing_items_default_to_empty():
    body = {k: v for k, v in SUB_BODY.items() if k != 'items'}
    client, _ = fake_client([{'status': 200, 'body': {'data': body}}])
    sub = client.subscriptions.cancel('000010', 1)
    assert sub.items == []


def test_pause_sends_pause_until_date():
    client, mock = fake_client([sub_response(status='Paused')])
    sub = client.subscriptions.pause('000010', 1, '2026-09-01')
    assert sub.status == 'Paused'
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 1, 'pause_until_date': '2026-09-01'}}
    assert mock.request.call_args.args[0] == 'PATCH'
    assert mock.request.call_args.args[1].endswith('subscription/pause')


def test_pause_without_date_omits_pause_until_date():
    client, mock = fake_client([sub_response(status='Paused')])
    client.subscriptions.pause('000010', 1)
    assert 'pause_until_date' not in sent_body(mock)['data']


@pytest.mark.parametrize('method', ['resume', 'cancel'])
def test_resume_and_cancel_use_patch(method):
    client, mock = fake_client([sub_response()])
    getattr(client.subscriptions, method)('000010', 1)
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_id': 1}}
    assert mock.request.call_args.args[0] == 'PATCH'
    assert mock.request.call_args.args[1].endswith(f'subscription/{method}')
