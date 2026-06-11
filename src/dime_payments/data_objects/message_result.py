from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class MessageResult:
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'MessageResult':
        return cls(message=arr_string(data, 'message'))
