from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class Address:
    id: int | None = None
    recipient: str | None = None
    line_one: str | None = None
    line_two: str | None = None
    line_three: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Address':
        return cls(
            # API returns address_id on show, id on list items.
            id=arr_int(data, 'address_id') or arr_int(data, 'id'),
            recipient=arr_string(data, 'recipient'),
            line_one=arr_string(data, 'line_one'),
            line_two=arr_string(data, 'line_two'),
            line_three=arr_string(data, 'line_three'),
            city=arr_string(data, 'city'),
            state=arr_string(data, 'state'),
            zip=arr_string(data, 'zip'),
        )
