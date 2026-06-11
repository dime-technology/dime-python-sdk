import pytest
from tests.helpers import fake_client, sent_body

DEPOSIT_BODY = {
    'transaction_date': '2026-01-15',
    'fund_date': '2026-01-17',
    'transaction_info_id': '100001',
    'net_amount': '49.99',
    'sweep_id': 'SWP-001',
    'type': 'CC',
}

DEPOSIT_WITH_TXN = {
    'sid': '000010',
    'sweep_id': 'SWP-001',
    'countOfTransactions': 3,
    'transTotal': '149.97',
    'transactions': [
        {'transaction_type': 'CC', 'transaction_status': 'Success', 'amount': '49.99', 'pending': False, 'billing_address': {}, 'shippingAddress': {}},
    ],
}


def test_list_returns_cursor_page():
    client, _ = fake_client([{'status': 200, 'body': {'data': [DEPOSIT_BODY], 'meta': {}}}])
    page = client.deposits.list('000010')
    assert len(page) == 1
    assert page.data[0].sweep_id == 'SWP-001'


def test_list_sends_filters():
    client, mock = fake_client([{'status': 200, 'body': {'data': [], 'meta': {}}}])
    client.deposits.list('000010', {'start_date': '2026-01-01'})
    body = sent_body(mock)
    assert body['filters']['start_date'] == '2026-01-01'


def test_list_with_transactions_returns_deposit_group():
    client, _ = fake_client([{'status': 200, 'body': {'data': {
        'sid': '000010',
        'count': 1,
        'deposits': {'SWP-001': DEPOSIT_WITH_TXN},
    }}}])
    group = client.deposits.list_with_transactions('000010', {'start_date': '2026-01-01', 'end_date': '2026-01-31'})
    assert group.count == 1
    assert len(group.deposits) == 1
    assert group.deposits[0].count_of_transactions == 3


def test_list_with_transactions_handles_array_deposits():
    client, _ = fake_client([{'status': 200, 'body': {'data': {
        'sid': '000010',
        'count': 1,
        'deposits': [DEPOSIT_WITH_TXN],
    }}}])
    group = client.deposits.list_with_transactions('000010', {'start_date': '2026-01-01', 'end_date': '2026-01-31'})
    assert len(group.deposits) == 1


def test_show_maps_deposit_with_transactions():
    client, _ = fake_client([{'status': 200, 'body': {'data': DEPOSIT_WITH_TXN}}])
    result = client.deposits.show('000010', {'sweep_id': 'SWP-001'})
    assert result.trans_total == '149.97'
    assert len(result.transactions) == 1
    assert result.transactions[0].amount == '49.99'


def test_show_transactions_handles_dict():
    client, _ = fake_client([{'status': 200, 'body': {'data': {
        **DEPOSIT_WITH_TXN,
        'transactions': {'1': DEPOSIT_WITH_TXN['transactions'][0]},
    }}}])
    result = client.deposits.show('000010', {'sweep_id': 'SWP-001'})
    assert len(result.transactions) == 1
