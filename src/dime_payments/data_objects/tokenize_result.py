from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_string


@dataclass
class TokenizeResult:
    token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TokenizeResult':
        return cls(token=arr_string(data, 'token'))
