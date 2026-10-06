import pytest
from dime_payments import ValidationException
from tests.helpers import fake_client, sent_body

PLAN_BODY = {
    'id': 1,
    'name': 'Monthly Membership',
    'description': None,
    'recurrence_schedule': 'Monthly',
    'status': 'active',
    'subtotal': 20,
    'total': 20,
    'token': 'aBQcMJFZVKtsYNC1CWfxca2tvwB1Ls52yMuzT7JI',
    'public_url': 'https://app.dimepayments.com/subscribe/aBQcMJFZVKtsYNC1CWfxca2tvwB1Ls52yMuzT7JI',
    'allow_public': True,
    'created_at': '2026-07-22T13:16:46-04:00',
    'items': [
        {'name': 'General', 'description': None, 'quantity': 2, 'unit_price': 10},
    ],
}


def plan_response(status=200):
    return {'status': status, 'body': {'data': PLAN_BODY}}


def test_list_returns_cursor_page():
    client, mock = fake_client([{'status': 200, 'body': {'data': [PLAN_BODY], 'meta': {}}}])
    page = client.subscription_plans.list('000010')
    assert page.data[0].name == 'Monthly Membership'
    assert page.data[0].allow_public is True
    assert page.data[0].items[0].unit_price == '10'
    assert page.data[0].items[0].amount is None
    assert mock.request.call_args.args[1].endswith('subscription-plan/list')


def test_list_sends_status_in_data_not_filters():
    client, mock = fake_client([{'status': 200, 'body': {'data': [PLAN_BODY], 'meta': {}}}])
    client.subscription_plans.list('000010', status='active')
    assert sent_body(mock) == {'data': {'sid': '000010', 'status': 'active'}}


def test_show_maps_response():
    client, mock = fake_client([plan_response()])
    plan = client.subscription_plans.show('000010', 1)
    assert plan.id == 1
    assert plan.total == '20'
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_plan_id': 1}}
    assert mock.request.call_args.args[0] == 'GET'


def test_create_sends_attributes():
    client, mock = fake_client([plan_response(201)])
    client.subscription_plans.create('000010', {
        'name': 'Monthly Membership',
        'recurrence_schedule': 'Monthly',
        'lines': [
            {'item_id': 5, 'name': 'Base membership', 'quantity': 1, 'unit_price': 25},
        ],
    })
    body = sent_body(mock)
    assert body['data']['recurrence_schedule'] == 'Monthly'
    assert body['data']['lines'][0]['item_id'] == 5
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('subscription-plan/create')


def test_edit_uses_patch_and_edit_path():
    client, mock = fake_client([plan_response()])
    client.subscription_plans.edit('000010', 42, {
        'name': 'Renamed',
        'recurrence_schedule': 'Yearly',
        'lines': [{'item_id': 5, 'name': 'Base', 'quantity': 1, 'unit_price': 25}],
    })
    body = sent_body(mock)
    assert body['data']['subscription_plan_id'] == 42
    assert body['data']['name'] == 'Renamed'
    assert mock.request.call_args.args[0] == 'PATCH'
    assert mock.request.call_args.args[1].endswith('subscription-plan/edit')


def test_delete_returns_message_result():
    client, mock = fake_client([
        {'status': 200, 'body': {'data': {'message': 'Subscription plan deleted'}}},
    ])
    result = client.subscription_plans.delete('000010', 42)
    assert result.message == 'Subscription plan deleted'
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('subscription-plan/delete')


def test_delete_with_subscribers_raises_with_message():
    client, _ = fake_client([{'status': 422, 'body': {'data': {
        'message': 'Cannot delete a plan with subscribers. Archive it instead.',
    }}}])
    with pytest.raises(ValidationException) as exc_info:
        client.subscription_plans.delete('000010', 42)
    assert str(exc_info.value) == 'Cannot delete a plan with subscribers. Archive it instead.'


@pytest.mark.parametrize('method', ['publish', 'archive', 'unarchive'])
def test_lifecycle_methods_use_patch(method):
    client, mock = fake_client([plan_response()])
    plan = getattr(client.subscription_plans, method)('000010', 42)
    assert plan.id == 1
    assert sent_body(mock) == {'data': {'sid': '000010', 'subscription_plan_id': 42}}
    assert mock.request.call_args.args[0] == 'PATCH'
    assert mock.request.call_args.args[1].endswith(f'subscription-plan/{method}')


def test_subscribe_returns_subscribe_result():
    client, mock = fake_client([{'status': 201, 'body': {'data': {
        'subscription_id': 10,
        'status': 'Active',
        'next_run_date': '2026-08-21',
        'transaction_number': 'TXN-123',
        'amount': 25,
    }}}])
    result = client.subscription_plans.subscribe('000010', 42, 'cust-uuid-1', 88)
    assert result.subscription_id == 10
    assert result.transaction_number == 'TXN-123'
    assert result.amount == '25'
    assert sent_body(mock) == {'data': {
        'sid': '000010',
        'subscription_plan_id': 42,
        'customer_uuid': 'cust-uuid-1',
        'payment_method': 88,
    }}
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('subscription-plan/subscribe')


def test_subscribe_declined_charge_raises():
    client, _ = fake_client([{'status': 422, 'body': {'data': {
        'message': 'Card declined',
        'transaction_number': None,
    }}}])
    with pytest.raises(ValidationException) as exc_info:
        client.subscription_plans.subscribe('000010', 42, 'cust-uuid-1', 88)
    assert str(exc_info.value) == 'Card declined'
