from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_int, arr_string


@dataclass
class PaymentMethod:
    id: int | None = None
    type: str | None = None
    token: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    cc_name_on_card: str | None = None
    cc_last_four: str | None = None
    cc_expiration_date: str | None = None
    cc_brand: str | None = None
    ach_bank_account_name: str | None = None
    ach_routing_number: str | None = None
    ach_account_number: str | None = None
    ach_ownership_type: str | None = None
    ach_account_type: str | None = None
    ach_bank_name: str | None = None
    status: str | None = None
    status_date: str | None = None
    enabled: bool = False
    is_default: bool = False
    addr1: str | None = None
    addr2: str | None = None
    addr3: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PaymentMethod':
        return cls(
            id=arr_int(data, 'id'),
            type=arr_string(data, 'type'),
            token=arr_string(data, 'token'),
            first_name=arr_string(data, 'first_name'),
            last_name=arr_string(data, 'last_name'),
            cc_name_on_card=arr_string(data, 'cc_name_on_card'),
            cc_last_four=arr_string(data, 'cc_last_four'),
            cc_expiration_date=arr_string(data, 'cc_expiration_date'),
            cc_brand=arr_string(data, 'cc_brand'),
            ach_bank_account_name=arr_string(data, 'ach_bank_account_name'),
            ach_routing_number=arr_string(data, 'ach_routing_number'),
            ach_account_number=arr_string(data, 'ach_account_number'),
            ach_ownership_type=arr_string(data, 'ach_ownership_type'),
            ach_account_type=arr_string(data, 'ach_account_type'),
            ach_bank_name=arr_string(data, 'ach_bank_name'),
            status=arr_string(data, 'status'),
            status_date=arr_string(data, 'status_date'),
            enabled=arr_bool(data, 'enabled'),
            is_default=arr_bool(data, 'default'),
            addr1=arr_string(data, 'addr1'),
            addr2=arr_string(data, 'addr2'),
            addr3=arr_string(data, 'addr3'),
            city=arr_string(data, 'city'),
            state=arr_string(data, 'state'),
            zip=arr_string(data, 'zip'),
        )
