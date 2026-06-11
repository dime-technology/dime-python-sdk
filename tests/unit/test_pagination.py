import pytest
from tests.helpers import fake_client


def txn_page(items: list, next_cursor: str | None = None):
    return {
        'status': 200,
        'body': {
            'data': items,
            'meta': {
                'next_cursor': next_cursor,
                'prev_cursor': None,
                'per_page': 500,
                'path': 'https://app.dimepayments.com/api/transactions',
            },
        },
    }


def item(amount: str) -> dict:
    return {
        'transaction_type': 'CC',
        'transaction_status': 'Success',
        'amount': amount,
        'pending': False,
        'billing_address': {},
        'shippingAddress': {},
    }


def test_has_more_false_on_last_page():
    client, _ = fake_client([txn_page([item('10.00')])])
    page = client.transactions.list('000010')
    assert page.has_more() is False
    assert page.next() is None


def test_has_more_true_when_next_cursor_set():
    client, _ = fake_client([txn_page([item('10.00')], 'cursor-abc')])
    page = client.transactions.list('000010')
    assert page.has_more() is True


def test_next_fetches_next_page():
    client, _ = fake_client([
        txn_page([item('10.00')], 'cursor-abc'),
        txn_page([item('20.00')]),
    ])
    page1 = client.transactions.list('000010')
    page2 = page1.next()
    assert page2 is not None
    assert page2.data[0].amount == '20.00'
    assert page2.has_more() is False


def test_auto_paging_yields_all_items():
    client, _ = fake_client([
        txn_page([item('1.00'), item('2.00')], 'cursor-p2'),
        txn_page([item('3.00'), item('4.00')]),
    ])
    page = client.transactions.list('000010')
    amounts = [txn.amount for txn in page.auto_paging()]
    assert amounts == ['1.00', '2.00', '3.00', '4.00']


def test_len_returns_item_count():
    client, _ = fake_client([txn_page([item('1.00'), item('2.00')])])
    page = client.transactions.list('000010')
    assert len(page) == 2


def test_for_loop_iterates_first_page():
    client, _ = fake_client([txn_page([item('5.00'), item('6.00')])])
    page = client.transactions.list('000010')
    amounts = [txn.amount for txn in page]
    assert amounts == ['5.00', '6.00']


def test_pages_without_meta_degrade_gracefully():
    client, _ = fake_client([{
        'status': 200,
        'body': {'data': [{'uuid': 'c1', 'first_name': 'Jane', 'last_name': 'Doe'}]},
    }])
    page = client.customers.list('000010')
    assert len(page.data) == 1
    assert page.has_more() is False
