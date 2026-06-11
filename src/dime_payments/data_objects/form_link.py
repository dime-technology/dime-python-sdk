from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class FormLink:
    link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FormLink':
        return cls(link=arr_string(data, 'link'))
