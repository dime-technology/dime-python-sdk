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
| `dime.transactions`             | charge_card, charge_card_token, charge_ach, authorize, capture, tokenize_card, refund, void, show, list |
| `dime.customers`                | list, show, create, update, delete                                    |
| `dime.payment_methods`          | list, show, create, update, delete                                    |
| `dime.merchants`                | list, show, create, update, get_form_link, application_status         |
| `dime.addresses`                | list, show, create, update, delete                                    |
| `dime.deposits`                 | list, list_with_transactions, show                                    |
| `dime.recurring_payments`       | list, show, create, edit, pause, cancel, activate, delete             |
| `dime.invoices`                 | list, show, create, update, delete, send, mark_sent, void, duplicate, pay, get_link, list_items, add_line_item, update_line_item, delete_line_item, create_item |
| `dime.recurring_invoices`       | list, show, create, cancel                                            |
| `dime.chargebacks`              | list, show                                                            |
| `dime.documents`                | upload, list                                                          |
| `dime.funds`                    | balance, transactions, release                                        |
| `dime.subscription_plans`       | list, show, create, edit, delete, publish, archive, unarchive, subscribe |
| `dime.subscriptions`            | list, show, pause, resume, cancel                                     |

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

#### Authorize now, capture later

`authorize()` holds the amount on the card without moving money. Pass its `transaction_number` to
`capture()` to collect, or to `void()` to release the hold. Capture promptly — the issuer drops an
uncaptured hold on its own schedule — and only once: a partial capture settles that amount and
releases the rest. Needs the `transaction:authorize-capture` ability.

```python
auth = dime.transactions.authorize('000010', {'amount': '100.00', 'token': 'tok_abc123'})

# Collect it: omit the amount to capture the full hold
dime.transactions.capture('000010', auth.transaction_number, '80.00')

# ...or release the hold instead
dime.transactions.void('000010', 'CC', auth.transaction_number)
```

### Merchant onboarding

Follow up an application sent with `get_form_link()`. `status` is the headline; while it is
`underwriting`, read `application_status` — only `needs_documents` asks you to act. `boarded` says
whether the merchant can take money. The `application_status_changed` webhook carries the same
fields, so poll only to reconcile.

```python
status = dime.merchants.application_status('000010')
print(status.status, status.application_status, status.boarded)
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

### Invoices

Invoices are scoped to a merchant `sid` and built from line items that each reference a merchant
item (a fund or designation). Draft invoices can be edited; once sent they are locked.

Identify the customer with `customer_uuid` — the same uuid every other resource uses, and the only
identifier the customer endpoints return. `customer_id` is still accepted for older integrations.

**Statuses.** `invoice.status` is one of `draft`, `sent`, `viewed`, `partially_paid`, `paid`, `void` or
`refunded`. `paid` is not always final: if the customer's bank returns an ACH payment, the invoice is
reopened (back to `partially_paid`, `viewed` or `sent`, with `amount_paid` and `balance` updated) and an
`invoice_payment_returned` webhook fires. Re-read the invoice rather than caching a `paid` status forever.

```python
# Look up (or create) the merchant items a line can reference
items = dime.invoices.list_items('000010')
item = dime.invoices.create_item('000010', {
    'name': 'Consulting',
    'description': 'Professional services',
    'price': 125,
    'tax_deductible': False,
})

# Create a draft invoice with one or more line items
invoice = dime.invoices.create('000010', {
    'customer_uuid': customer.uuid,
    'customer_name': 'Jane Doe',
    'customer_email': 'jane@example.com',
    'payment_terms': 'net_15',  # due_on_receipt | net_15 | net_30 | net_60
    'lines': [
        {'item_id': item.id, 'name': 'Consulting', 'description': '2 hours',
         'quantity': 2, 'unit_price': 125},
    ],
})

# Line-item edits return the refreshed invoice, with totals recalculated
invoice = dime.invoices.add_line_item('000010', invoice.id, {
    'item_id': item.id, 'name': 'Setup', 'quantity': 1, 'unit_price': 50,
})
invoice = dime.invoices.update_line_item('000010', invoice.id, invoice.items[0].id, {'quantity': 3})
invoice = dime.invoices.delete_line_item('000010', invoice.id, invoice.items[0].id)

# Email it to the customer, or activate the pay link without emailing
dime.invoices.send('000010', invoice.id)
dime.invoices.mark_sent('000010', invoice.id)

# Share the public pay link
link = dime.invoices.get_link('000010', invoice.id)
print(link.public_url)

# Take a merchant-initiated payment. payment_type is required; omit amount to
# pay the full balance.
dime.invoices.pay('000010', invoice.id, {
    'payment_type': 'cc',  # cc | ach
    'token': pm.token,
    'amount': 125,
})

dime.invoices.void('000010', invoice.id)
dime.invoices.duplicate('000010', invoice.id)
```

#### Making the customer cover processing fees

Set `cover_fee_required` and the customer must pay the processing fee — it is not an optional
checkbox at checkout. The fee is **not** a line item and is **not** part of `total`: the merchant is
still owed `total`, and the fee is added on top of whatever the customer pays.

Card and ACH rates differ, so the charge depends on how the customer pays. `cover_fee_quote` gives
you both, quoted against the outstanding balance:

```python
invoice = dime.invoices.create('000010', {
    'customer_uuid': customer.uuid,
    'customer_name': 'Jane Doe',
    'customer_email': 'jane@example.com',
    'payment_terms': 'net_15',
    'cover_fee_required': True,  # omit to inherit the merchant's invoice setting
    'lines': [
        {'item_id': item.id, 'name': 'Consulting', 'quantity': 1, 'unit_price': 100},
    ],
})

invoice.total                      # '100.00' — what the merchant is owed
invoice.cover_fee_quote.cc_total   # '104.32' — charged if they pay by card
invoice.cover_fee_quote.ach_total  # '101.26' — charged if they pay by bank
```

The card figure is the higher of the two and is what the invoice and its emails lead with. A partial
payment re-quotes the fee against the partial amount, so treat the quote as "settling in full today"
rather than a fixed charge. `cover_fee_quote` is `None` when no fee is required.

To reconcile a payment, `amount` was credited to the invoice and `cover_fee` was charged on top:

```python
payment = invoice.payments[0]
payment.amount     # '100.00' — applied to the balance
payment.cover_fee  # '4.32'   — the fee the customer also paid
# The customer was charged amount + cover_fee.
```

`pay()` behaves the same way: the fee for the `payment_type` you pass is added to `amount`, so the
card or bank account is debited more than the invoice is credited.

### Recurring invoices

Templates that emit an invoice on a schedule. `cover_fee_required` is copied onto every invoice a
template generates.

```python
ri = dime.recurring_invoices.create('000010', {
    'customer_uuid': customer.uuid,
    'payment_terms': 'net_30',
    'recurring_frequency': 'Monthly',  # Weekly | Biweekly | FirstFifteenth | Monthly | Yearly
    'recurring_start_date': '2026-09-01',
    'cover_fee_required': True,  # optional
    'lines': [
        {'item_id': item.id, 'name': 'Retainer', 'quantity': 1, 'unit_price': 500},
    ],
})

print(ri.next_run_date, ri.upcoming_run_dates)

dime.recurring_invoices.cancel('000010', ri.id)
```

### Chargebacks and documents

Chargebacks arrive from the processor once a day; the chargeback webhooks tell you when one opens or
changes, and these endpoints let you reconcile. Contest one by uploading evidence as a
`RetrievalRequest` document against its `transaction_info_id`.

```python
for cb in dime.chargebacks.list('000010', {'representment_status': 'New'}).auto_paging():
    print(cb.transaction_info_id, cb.chargeback_amount, cb.representment_date)

cb = dime.chargebacks.show('000010', '8675309')

# Each file is a path or a (filename, bytes-or-file-object) pair. Up to 10 per call,
# 9 MB each, as PDF, JPG, PNG, DOC, DOCX or RTF.
result = dime.documents.upload(
    '000010',
    'RetrievalRequest',  # Verification | FraudHolds | Underwriting | RetrievalRequest
    ['receipt.pdf', ('signature.png', png_bytes)],
    chargeback_transaction_info_id=cb.transaction_info_id,
)
for failure in result.failed:  # files are stored independently; re-send only these
    print(failure.file_name, failure.reason)

docs = dime.documents.list('000010', {'chargeback_transaction_info_id': cb.transaction_info_id})
```

`upload()` is the one `multipart/form-data` request in the API; the SDK builds it for you. Uploading
does not forward anything to the processor — Dime reviews the documents and sends them on.

### Held funds

For merchants on a tier that holds their balance rather than sweeping it to the bank. Any other
merchant gets a `ValidationException` (422). Reading needs `funds:read`; releasing needs
`funds:release` on an affiliate key.

```python
balance = dime.funds.balance('000010')
print(balance.available, balance.releasable)  # release against releasable

# Release by amount...
result = dime.funds.release('000010', 'payout-2026-10-06-0001', amount='1500.00')

# ...or by payment, all or nothing
payable = dime.funds.transactions('000010')
result = dime.funds.release(
    '000010',
    'payout-2026-10-06-0002',
    transaction_info_ids=[t.transaction_info_id for t in payable.transactions],
)

print(result.release.status)  # released | unknown
```

Use a fresh `idempotency_key` for every intended release and reuse it when retrying: a repeat
returns the original release (`result.replayed`) instead of sending money twice. `unknown` means no
confirmation came back and it may have gone through; its amount stays out of `releasable` until it
is reconciled, so a later release cannot pay it twice. A declined
release raises `ValidationException`, with the failed record under
`e.get_response_body()['data']['release']`; a reused key or a release already in flight raises
`ApiException` (409).

### Subscription plans and subscriptions

A plan is a recurring offering built from merchant items. Create it as a draft, publish it, then
subscribe customers to it; each subscriber keeps their own snapshot, so later edits do not change
what they pay.

```python
plan = dime.subscription_plans.create('000010', {
    'name': 'Monthly Membership',
    'recurrence_schedule': 'Monthly',  # Weekly | Biweekly | FirstFifteenth | Monthly | Yearly
    'lines': [
        {'item_id': item.id, 'name': 'Base membership', 'quantity': 1, 'unit_price': 25},
    ],
})
dime.subscription_plans.publish('000010', plan.id)

# Charges the first payment now; a decline raises ValidationException
result = dime.subscription_plans.subscribe('000010', plan.id, customer.uuid, pm.id)

sub = dime.subscriptions.show('000010', result.subscription_id)
dime.subscriptions.pause('000010', sub.id, '2026-12-01')  # omit the date to pause indefinitely
dime.subscriptions.resume('000010', sub.id)
dime.subscriptions.cancel('000010', sub.id)

# edit() replaces the plan wholesale, so send every field and line
dime.subscription_plans.edit('000010', plan.id, {
    'name': 'Monthly Membership',
    'recurrence_schedule': 'Monthly',
    'lines': [{'item_id': item.id, 'name': 'Base membership', 'quantity': 1, 'unit_price': 30}],
})
dime.subscription_plans.archive('000010', plan.id)  # stop new sign-ups; unarchive() to reopen as a draft
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

The exception message is the API's own where it sends one. Some list endpoints answer `404` when
nothing matches: an empty chargeback, document or subscription list raises `NotFoundException`.

## Notes

- **GET requests carry a JSON body.** The Dime API expects read parameters in the request body
  even for `GET` endpoints; the SDK handles this transparently. Point `base_url` at an `https://`
  origin — an `http://` URL that 301-redirects to `https` will have its request body dropped by the
  redirect, which surfaces as a `403` "You do not have access to this company." from the API.
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
