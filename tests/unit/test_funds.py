import pytest
from dime_payments import ApiException, ValidationException
from tests.helpers import fake_client, sent_body

BALANCE_BODY = {
    'sid': '91828382',
    'available': 6492.87,
    'pending': 0,
    'reserve': 0,
    'at_risk': 1250,
    'owed_to_split': 40.15,
    'unresolved': 0,
    'release_fee': 30,
    'releasable': 5172.72,
    'ach_settlement_days': 7,
    'ach_out_enabled': True,
    'ach_out_limit_remaining': 19999999.99,
}

RELEASE_BODY = {
    'sid': '91828382',
    'replayed': False,
    'release': {
        'id': 42,
        'amount': 1500,
        'fee': 30,
        'status': 'released',
        'status_label': 'Released',
        'idempotency_key': 'payout-2026-09-25-0001',
        'transaction_info_ids': None,
        'failure_reason': None,
        'requested_at': '2026-09-25T14:02:11+00:00',
        'completed_at': '2026-09-25T14:02:12+00:00',
    },
}


def test_balance_maps_response():
    client, mock = fake_client([{'status': 200, 'body': {'data': BALANCE_BODY}}])
    balance = client.funds.balance('91828382')
    assert balance.releasable == '5172.72'
    assert balance.at_risk == '1250'
    assert balance.ach_settlement_days == 7
    assert balance.ach_out_enabled is True
    assert sent_body(mock) == {'data': {'sid': '91828382'}}
    assert mock.request.call_args.args[0] == 'GET'
    assert mock.request.call_args.args[1].endswith('funds/balance')


def test_balance_for_merchant_without_held_funds_raises():
    client, _ = fake_client([{'status': 422, 'body': {'data': {
        'message': "This merchant's funds are not held; they settle automatically.",
    }}}])
    with pytest.raises(ValidationException) as exc_info:
        client.funds.balance('91828382')
    assert str(exc_info.value) == "This merchant's funds are not held; they settle automatically."


def test_transactions_maps_response():
    client, mock = fake_client([{'status': 200, 'body': {'data': {
        'sid': '91828382',
        'transactions': [{
            'transaction_info_id': '1297431',
            'type': 'CC',
            'transaction_date': '2026-09-28T15:12:09+00:00',
            'gross_amount': 100,
            'net_amount': 97,
            'split_amount': 1.25,
            'amount': 95.75,
        }],
        'total': 95.75,
        'truncated': False,
    }}}])
    result = client.funds.transactions('91828382')
    assert result.transactions[0].transaction_info_id == '1297431'
    assert result.transactions[0].amount == '95.75'
    assert result.total == '95.75'
    assert result.truncated is False
    assert mock.request.call_args.args[1].endswith('funds/transactions')


def test_release_by_amount():
    client, mock = fake_client([{'status': 201, 'body': {'data': RELEASE_BODY}}])
    result = client.funds.release('91828382', 'payout-2026-09-25-0001', amount='1500.00')
    assert result.replayed is False
    assert result.release.id == 42
    assert result.release.status == 'released'
    assert result.release.fee == '30'
    assert result.release.transaction_info_ids == []
    assert sent_body(mock) == {'data': {
        'sid': '91828382',
        'amount': '1500.00',
        'idempotency_key': 'payout-2026-09-25-0001',
    }}
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('funds/release')


def test_release_by_transactions():
    release = RELEASE_BODY['release'] | {'transaction_info_ids': ['1297431', '1297455']}
    client, mock = fake_client([{'status': 201, 'body': {'data': RELEASE_BODY | {'release': release}}}])
    result = client.funds.release('91828382', 'payout-2', transaction_info_ids=['1297431', '1297455'])
    assert result.release.transaction_info_ids == ['1297431', '1297455']
    assert sent_body(mock) == {'data': {
        'sid': '91828382',
        'transaction_info_ids': ['1297431', '1297455'],
        'idempotency_key': 'payout-2',
    }}


def test_release_unconfirmed_returns_unknown_status():
    release = RELEASE_BODY['release'] | {'status': 'unknown', 'failure_reason': 'No confirmation from the processor.'}
    client, _ = fake_client([{'status': 202, 'body': {'data': RELEASE_BODY | {'release': release}}}])
    result = client.funds.release('91828382', 'payout-3', amount=10)
    assert result.release.status == 'unknown'
    assert result.release.failure_reason == 'No confirmation from the processor.'


def test_release_declined_raises_with_failed_release_in_body():
    release = RELEASE_BODY['release'] | {'status': 'failed', 'failure_reason': 'Insufficient funds'}
    client, _ = fake_client([{'status': 422, 'body': {'data': RELEASE_BODY | {'release': release}}}])
    with pytest.raises(ValidationException) as exc_info:
        client.funds.release('91828382', 'payout-4', amount=10)
    assert exc_info.value.get_response_body()['data']['release']['status'] == 'failed'


def test_release_key_conflict_raises_api_exception_with_message():
    client, _ = fake_client([{'status': 409, 'body': {'data': {
        'message': 'Another release for this merchant is in progress. Try again in a moment.',
    }}}])
    with pytest.raises(ApiException) as exc_info:
        client.funds.release('91828382', 'payout-5', amount=10)
    assert exc_info.value.status_code == 409
    assert str(exc_info.value) == 'Another release for this merchant is in progress. Try again in a moment.'
