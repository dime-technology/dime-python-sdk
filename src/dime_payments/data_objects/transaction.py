from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_bool, arr_object_from, arr_string
from .transaction_address import TransactionAddress


@dataclass
class Transaction:
    transaction_type: str | None = None
    transaction_status: str | None = None
    transaction_status_description: str | None = None
    transaction_number: str | None = None
    transaction_date: str | None = None
    fund_date: str | None = None
    settle_date: str | None = None
    amount: str | None = None
    description: str | None = None
    status_code: str | None = None
    status_text: str | None = None
    email: str | None = None
    phone: str | None = None
    customer_uuid: str | None = None
    multi_use_token: str | None = None
    pending: bool = False
    transaction_info_id: str | None = None
    parent_transaction_info_id: str | None = None
    billing_address: TransactionAddress = field(default_factory=TransactionAddress)
    shipping_address: TransactionAddress = field(default_factory=TransactionAddress)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Transaction':
        return cls(
            transaction_type=arr_string(data, 'transaction_type'),
            transaction_status=arr_string(data, 'transaction_status'),
            transaction_status_description=arr_string(data, 'transaction_status_description'),
            transaction_number=arr_string(data, 'transaction_number'),
            transaction_date=arr_string(data, 'transaction_date'),
            fund_date=arr_string(data, 'fund_date'),
            settle_date=arr_string(data, 'settle_date'),
            amount=arr_string(data, 'amount'),
            description=arr_string(data, 'description'),
            status_code=arr_string(data, 'status_code'),
            status_text=arr_string(data, 'status_text'),
            email=arr_string(data, 'email'),
            phone=arr_string(data, 'phone'),
            customer_uuid=arr_string(data, 'customer_uuid'),
            multi_use_token=arr_string(data, 'multi_use_token'),
            pending=arr_bool(data, 'pending'),
            transaction_info_id=arr_string(data, 'transaction_info_id'),
            parent_transaction_info_id=arr_string(data, 'parent_transaction_info_id'),
            billing_address=TransactionAddress.from_dict(arr_object_from(data, ['billing_address'])),
            # API sometimes returns shipping under camelCase key; accept both.
            shipping_address=TransactionAddress.from_dict(
                arr_object_from(data, ['shippingAddress', 'shipping_address'])
            ),
        )
