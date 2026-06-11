from typing import Any


def arr_string(data: dict[str, Any], key: str, default: str | None = None) -> str | None:
    value = data.get(key)
    if value is None or isinstance(value, (dict, list)):
        return default
    if isinstance(value, bool):
        return '1' if value else '0'
    return str(value)


def arr_string_from(data: dict[str, Any], keys: list[str], default: str | None = None) -> str | None:
    for key in keys:
        if key in data and data[key] is not None:
            return arr_string(data, key, default)
    return default


def arr_int(data: dict[str, Any], key: str, default: int | None = None) -> int | None:
    value = data.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def arr_float(data: dict[str, Any], key: str, default: float | None = None) -> float | None:
    value = data.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def arr_bool(data: dict[str, Any], key: str, default: bool = False) -> bool:
    value = data.get(key)
    return default if value is None else bool(value)


def arr_object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def arr_object_from(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return {}


def arr_array(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    return value if isinstance(value, list) else []
