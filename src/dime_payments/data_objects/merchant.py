from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_bool, arr_string


@dataclass
class Merchant:
    name: str | None = None
    sid: str | None = None
    mcc: str | None = None
    slug: str | None = None
    pub_api_key: str | None = None
    processor_mid: str | None = None
    active: bool = False
    active_at: str | None = None
    g_pay: bool = False
    a_pay: bool = False
    pci_compliance: bool = False
    website: str | None = None
    addr1: str | None = None
    addr2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    phone: str | None = None
    primary_phone: str | None = None
    primary_email: str | None = None
    primary_name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Merchant':
        return cls(
            name=arr_string(data, 'name'),
            sid=arr_string(data, 'sid'),
            mcc=arr_string(data, 'mcc'),
            slug=arr_string(data, 'slug'),
            pub_api_key=arr_string(data, 'pub_api_key'),
            processor_mid=arr_string(data, 'processor_mid'),
            active=arr_bool(data, 'active'),
            active_at=arr_string(data, 'active_at'),
            g_pay=arr_bool(data, 'g_pay'),
            a_pay=arr_bool(data, 'a_pay'),
            pci_compliance=arr_bool(data, 'pci_compliance'),
            website=arr_string(data, 'website'),
            addr1=arr_string(data, 'addr1'),
            addr2=arr_string(data, 'addr2'),
            city=arr_string(data, 'city'),
            state=arr_string(data, 'state'),
            zip=arr_string(data, 'zip'),
            phone=arr_string(data, 'phone'),
            primary_phone=arr_string(data, 'primary_phone'),
            primary_email=arr_string(data, 'primary_email'),
            primary_name=arr_string(data, 'primary_name'),
        )
