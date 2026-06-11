from typing import Any
from unittest.mock import MagicMock

from dime_payments import Client
from dime_payments.config import Config


def make_mock_response(status: int, body: dict[str, Any], headers: dict[str, str] | None = None) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.json.return_value = body
    mock.headers = headers or {}
    return mock


def fake_client(responses: list[dict[str, Any]]) -> tuple[Client, MagicMock]:
    mock_session = MagicMock()
    mock_session.request.side_effect = [
        make_mock_response(r['status'], r['body'], r.get('headers'))
        for r in responses
    ]

    config = Config(token='test-token', session=mock_session, sleep=lambda _: None)
    client = Client(config)
    return client, mock_session


def sent_body(mock_session: MagicMock) -> dict[str, Any] | None:
    return mock_session.request.call_args.kwargs.get('json')
