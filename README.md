# Dime Payments Python SDK

A typed Python client for the [Dime Payments](https://dimepayments.com) API.
Works with Python 3.10+ on any platform.

```python
from dime_payments import Client

dime = Client('your-api-token')

txn = dime.transactions.charge_card('000010', {
    'amount': '49.99',
    'token': 'tok_abc123',
})

print(txn.transaction_status)  # "Success"
```

## Requirements

- Python 3.10+
- A Dime API token (a Laravel Sanctum personal access token). Tokens are minted inside the
  Dime application, not via this SDK, and carry abilities (e.g. `transaction:charge-card-token`,
  `customer:read`) that gate which calls succeed.

## Installation

```bash
pip install dime-python-sdk
```

## Configuration

The simplest setup needs only a token:

```python
dime = Client('your-api-token')
```

Point it at another environment, or use `Config` for full control:

```python
from dime_payments import Client, Config

# Staging environment
dime = Client('your-api-token', 'https://staging.dimepayments.com')

# Full control
dime = Client(Config(
    token='your-api-token',
    base_url='https://app.dimepayments.com',
    timeout=30.0,       # seconds
    max_retries=2,      # retries 429 / 5xx / network errors with backoff
    retry_base_delay=0.5,
))
```

The SDK sends `Authorization: Bearer <token>` and JSON headers on every request. Transient
failures (HTTP 429 and 5xx, network errors) are retried with exponential backoff, honoring the
`Retry-After` header when present.

## Resources

Every resource hangs off the client as a property. The merchant `sid` is always passed
explicitly; remaining fields go in an `attributes` or `filters` dict. All amounts are
returned as strings to avoid float rounding.

| Property                        | Endpoints                                                             |
| ------------------------------- | --------------------------------------------------------------------- |
| `dime.transactions`             | charge_card, charge_ach, tokenize_card, refund, void, show, list     |
| `dime.customers`                | list, show, create, update, delete                                    |
| `dime.payment_methods`          | list, show, create, update, delete                                    |
| `dime.merchants`                | list, show, create, update, get_form_link                             |
| `dime.addresses`                | list, show, create, update, delete                                    |
| `dime.deposits`                 | list, list_with_transactions, show                                    |
| `dime.recurring_payments`       | list, show, create, edit, pause, cancel, activate, delete             |

### Transactions

```python
# Charge a stored token
txn = dime.transactions.charge_card('000010', {
    'amount': '100.00',
    'token': 'tok_abc123',
    'email': 'customer@example.com',
})

# Charge raw card details (merchant must be PCI compliant)
txn = dime.transactions.charge_card('000010', {
    'amount': '100.00',
    'cardholder_name': 'John Doe',
    'card_number': '4111111111111111',
    'expiration_date': '01/2027',
    'cvv': '123',
})

# ACH
txn = dime.transactions.charge_ach('000010', {
    'routing_number': '123456789',
    'account_number': '9876543210',
    'account_type': 'Checking',
    'account_name': 'John Doe',
    'amount': '75.00',
})

# Tokenize without charging
result = dime.transactions.tokenize_card('000010', {
    'cardholder_name': 'John Doe',
    'card_number': '4111111111111111',
    'expiration_date': '01/2027',
})
print(result.token)

# Refund / void
dime.transactions.refund('000010', {'amount': '25.00', 'transaction_info_id': 123456})
dime.transactions.void('000010', 'CC', 123456)

# Read
txn = dime.transactions.show('000010', {'transaction_info_id': 123456})
```

### Customers, payment methods, addresses

```python
customer = dime.customers.create('000010', {
    'first_name': 'Jane',
    'last_name': 'Doe',
    'email': 'jane@example.com',
})

pm = dime.payment_methods.create('000010', {
    'uuid': customer.uuid,
    'type': 'cc',
    'cc_name_on_card': 'Jane Doe',
    'cc_number': '4111111111111111',
    'cc_expiration_date': '01/2027',
    'cc_brand': 'Visa',
    'default': True,
})

address = dime.addresses.create('000010', customer.uuid, {
    'recipient': 'Jane Doe',
    'line_one': '123 Main St',
    'city': 'Atlanta',
    'state': 'GA',
    'zip': '30301',
})
```

### Recurring payments

```python
rp = dime.recurring_payments.create('000010', {
    'name': 'Monthly donation',
    'amount': '25.00',
    'start_date': '2026-07-01 00:00:00',
    'recurrence_schedule': 'Monthly',
    'payment_method': pm.id,
    'customer_uuid': customer.uuid,
})

dime.recurring_payments.pause('000010', rp.id, '2026-09-01 00:00:00')
dime.recurring_payments.activate('000010', rp.id)
dime.recurring_payments.cancel('000010', rp.id)
```

## Pagination

List endpoints return a `CursorPage`. Iterate one page, walk pages manually, or stream every
item across all pages with `auto_paging()`:

```python
page = dime.transactions.list('000010', {
    'start_date': '2026-01-01 00:00:00',
    'end_date': '2026-01-31 23:59:59',
})

# First page only
for txn in page:
    print(txn.amount)

# Next page manually
if page.has_more():
    next_page = page.next()

# Every transaction across every page (fetches lazily)
for txn in page.auto_paging():
    print(txn.transaction_number)
```

## Error handling

Every failure raises a `DimeException` subclass. Catch the base type, or a specific one:

```python
from dime_payments import (
    DimeException,
    ValidationException,
    RateLimitException,
)
import time

try:
    dime.transactions.charge_card('000010', {'amount': '0'})
except ValidationException as e:
    e.get_errors()   # {'data.amount': ['must be greater than 0']}
    e.first_error()
except RateLimitException as e:
    wait = e.get_retry_after() or 1
    time.sleep(wait)
except DimeException as e:
    e.get_status_code()    # HTTP status
    e.get_response_body()  # decoded API body
```

| Exception                    | When                                                         |
| ---------------------------- | ------------------------------------------------------------ |
| `ValidationException`        | HTTP 400/422 with field errors                               |
| `AuthenticationException`    | HTTP 401 (missing/invalid token)                             |
| `PermissionDeniedException`  | HTTP 403 (belongs-to-company guard)                          |
| `NotFoundException`          | HTTP 404                                                     |
| `RateLimitException`         | HTTP 429 (carries `Retry-After`)                             |
| `ServerException`            | HTTP 5xx                                                     |
| `ConnectionException`        | No HTTP response (DNS, timeout, network error)               |
| `ApiException`               | Any other non-2xx                                            |

## Notes

- **GET requests carry a JSON body.** The Dime API expects read parameters in the request body
  even for `GET` endpoints; the SDK handles this transparently.
- **No API versioning.** Endpoints live under `/api` with no version prefix.

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest                  # run tests
```

## License

MIT. See [LICENSE](LICENSE).
