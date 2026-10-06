from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_int, arr_string


@dataclass
class Chargeback:
    """
    A chargeback raised against a merchant. The same field set the chargeback
    webhooks carry.

    ``transaction_info_id`` is the processor's stable identifier for the
    chargeback; ``parent_transaction_info_id`` identifies the disputed payment.
    ``representment_status`` and ``result`` are free text from the processor;
    ``resolved`` says whether the dispute has reached a terminal state.
    """

    transaction_info_id: str | None = None
    parent_transaction_info_id: str | None = None
    gateway_transaction_id: str | None = None
    transaction_number: str | None = None
    invoice_number: str | None = None
    chargeback_date: str | None = None
    merchant_chargeback_date: str | None = None
    transaction_amount: str | None = None
    chargeback_amount: str | None = None
    card_brand: str | None = None
    cc_last_four: str | None = None
    payee_name: str | None = None
    days_to_represent: int | None = None
    representment_date: str | None = None
    merchant_representment_date: str | None = None
    representment_status: str | None = None
    result: str | None = None
    chargeback_code: str | None = None
    chargeback_response_code: str | None = None
    resolved: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Chargeback':
        return cls(
            transaction_info_id=arr_string(data, 'transaction_info_id'),
            parent_transaction_info_id=arr_string(data, 'parent_transaction_info_id'),
            gateway_transaction_id=arr_string(data, 'gateway_transaction_id'),
            transaction_number=arr_string(data, 'transaction_number'),
            invoice_number=arr_string(data, 'invoice_number'),
            chargeback_date=arr_string(data, 'chargeback_date'),
            merchant_chargeback_date=arr_string(data, 'merchant_chargeback_date'),
            transaction_amount=arr_string(data, 'transaction_amount'),
            chargeback_amount=arr_string(data, 'chargeback_amount'),
            card_brand=arr_string(data, 'card_brand'),
            cc_last_four=arr_string(data, 'cc_last_four'),
            payee_name=arr_string(data, 'payee_name'),
            days_to_represent=arr_int(data, 'days_to_represent'),
            representment_date=arr_string(data, 'representment_date'),
            merchant_representment_date=arr_string(data, 'merchant_representment_date'),
            representment_status=arr_string(data, 'representment_status'),
            result=arr_string(data, 'result'),
            chargeback_code=arr_string(data, 'chargeback_code'),
            chargeback_response_code=arr_string(data, 'chargeback_response_code'),
            resolved=arr_bool(data, 'resolved'),
        )
