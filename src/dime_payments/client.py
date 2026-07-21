from .config import Config
from .http.transport import Transport
from .resources.addresses import Addresses
from .resources.customers import Customers
from .resources.deposits import Deposits
from .resources.invoices import Invoices
from .resources.merchants import Merchants
from .resources.payment_methods import PaymentMethods
from .resources.recurring_invoices import RecurringInvoices
from .resources.recurring_payments import RecurringPayments
from .resources.transactions import Transactions


class Client:
    def __init__(self, token: str | Config, base_url: str = Config.DEFAULT_BASE_URL) -> None:
        if isinstance(token, Config):
            self._config = token
        else:
            self._config = Config(token=token, base_url=base_url)

        transport = Transport(self._config)

        self.transactions = Transactions(transport)
        self.customers = Customers(transport)
        self.payment_methods = PaymentMethods(transport)
        self.merchants = Merchants(transport)
        self.addresses = Addresses(transport)
        self.deposits = Deposits(transport)
        self.recurring_payments = RecurringPayments(transport)
        self.invoices = Invoices(transport)
        self.recurring_invoices = RecurringInvoices(transport)

    def config(self) -> Config:
        return self._config
