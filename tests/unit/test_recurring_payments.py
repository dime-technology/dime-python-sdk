import pytest
from dime_payments.data_objects import RecurringPaymentItem
from tests.helpers import fake_client, sent_body

RP_BODY = {
    'id': 5,
    'name': 'Monthly donation',
    'amount': '25.00',
    'start_date': '2026-07-01 00:00:00',
    'recurrence_schedule': 'Monthly',
    'status': 'Active',
    'payment_method': {'id': 42, 'type': 'cc'},
    'shipping_address': {},
}


def rp_response():
    return {'status': 200, 'body': {'data': RP_BODY}}


def test_create_maps_response():
    client, _ = fake_client([rp_response()])
    rp = client.recurring_payments.create('000010', {
        'name': 'Monthly donation',
        'amount': '25.00',
        'start_date': '2026-07-01 00:00:00',
        'recurrence_schedule': 'Monthly',
        'payment_method': 42,
        'customer_uuid': 'cust-uuid-1',
    })
    assert rp.id == 5
    assert rp.amount == '25.00'
    assert rp.payment_method.id == 42


def test_pause_sends_pause_until_date():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.pause('000010', 5, '2026-09-01 00:00:00')
    body = sent_body(mock)
    assert body == {'data': {'sid': '000010', 'recurring_payment_id': 5, 'pause_until_date': '2026-09-01 00:00:00'}}


def test_pause_without_date_omits_pause_until_date():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.pause('000010', 5)
    body = sent_body(mock)
    assert 'pause_until_date' not in body.get('data', {})


def test_cancel_sends_patch_to_correct_path():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.cancel('000010', 5)
    assert 'recurring-payment/cancel' in mock.request.call_args.args[1]


def test_activate_sends_patch():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.activate('000010', 5)
    assert mock.request.call_args.args[0] == 'PATCH'


def test_delete_returns_message():
    client, _ = fake_client([{'status': 200, 'body': {'data': {'message': 'Deleted'}}}])
    result = client.recurring_payments.delete('000010', 5)
    assert result.message == 'Deleted'


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [RP_BODY], 'meta': {}}}])
    page = client.recurring_payments.list('000010')
    assert page.data[0].name == 'Monthly donation'


def test_edit_sends_recurring_payment_id():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.edit('000010', 5, {'amount': '30.00'})
    body = sent_body(mock)
    assert body['data']['recurring_payment_id'] == 5
    assert body['data']['amount'] == '30.00'


def test_reads_the_pinned_item_and_the_covered_fee():
    client, _ = fake_client([{'status': 200, 'body': {'data': RP_BODY | {
        'cover_processing_amount': '0.75',
        'item': {'id': 42, 'name': 'Building Fund'},
    }}}])
    rp = client.recurring_payments.show('000010', 5)
    assert rp.cover_processing_amount == '0.75'
    assert isinstance(rp.item, RecurringPaymentItem)
    assert rp.item.id == 42
    assert rp.item.name == 'Building Fund'


def test_reads_an_unpinned_payment_as_no_item():
    client, _ = fake_client([{'status': 200, 'body': {'data': RP_BODY | {'cover_processing_amount': None, 'item': None}}}])
    rp = client.recurring_payments.show('000010', 5)
    assert rp.item is None
    assert rp.cover_processing_amount is None


def test_keeps_an_item_id_whose_name_is_not_disclosed():
    client, _ = fake_client([{'status': 200, 'body': {'data': RP_BODY | {'item': {'id': 42, 'name': None}}}}])
    rp = client.recurring_payments.show('000010', 5)
    assert rp.item is not None
    assert rp.item.id == 42
    assert rp.item.name is None


def test_create_sends_item_id_and_customer_covers_fee():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.create('000010', {
        'name': 'Monthly donation',
        'amount': '25.00',
        'start_date': '2026-07-01 00:00:00',
        'recurrence_schedule': 'Monthly',
        'payment_method': 42,
        'customer_uuid': 'cust-uuid-1',
        'customer_covers_fee': True,
        'item_id': 42,
    })
    data = sent_body(mock)['data']
    assert data['customer_covers_fee'] is True
    assert data['item_id'] == 42


def test_edit_sends_a_none_item_id_to_unpin_and_still_drops_other_nones():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.edit('000010', 5, {'item_id': None, 'name': None})
    assert sent_body(mock) == {'data': {'sid': '000010', 'recurring_payment_id': 5, 'item_id': None}}


def test_edit_leaves_item_id_out_when_it_is_not_given():
    client, mock = fake_client([rp_response()])
    client.recurring_payments.edit('000010', 5, {'amount': '30.00'})
    assert sent_body(mock) == {'data': {'sid': '000010', 'recurring_payment_id': 5, 'amount': '30.00'}}
