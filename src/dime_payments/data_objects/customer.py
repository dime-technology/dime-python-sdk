from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class Customer:
    uuid: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    addr1: str | None = None
    addr2: str | None = None
    addr3: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Customer':
        return cls(
            uuid=arr_string(data, 'uuid'),
            first_name=arr_string(data, 'first_name'),
            last_name=arr_string(data, 'last_name'),
            phone=arr_string(data, 'phone'),
            email=arr_string(data, 'email'),
            addr1=arr_string(data, 'addr1'),
            addr2=arr_string(data, 'addr2'),
            addr3=arr_string(data, 'addr3'),
            city=arr_string(data, 'city'),
            state=arr_string(data, 'state'),
            zip=arr_string(data, 'zip'),
            country=arr_string(data, 'country'),
        )
