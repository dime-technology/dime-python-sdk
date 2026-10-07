import io

import pytest
from tests.helpers import fake_client, sent_body

UPLOAD_BODY = {
    'message': '1 document uploaded. 1 could not be stored.',
    'documents': [
        {'uuid': '9b1c-uuid', 'file_name': 'receipt.pdf', 'doc_type': 'RetrievalRequest', 'size': 20841},
    ],
    'failed': [
        {'file_name': 'statement.pdf', 'reason': 'The file could not be stored. Send it again.'},
    ],
}

DOCUMENT_BODY = {
    'uuid': '9b1c-uuid',
    'file_name': 'receipt.pdf',
    'doc_type': 'RetrievalRequest',
    'chargeback_transaction_info_id': '8675309',
    'size': 20841,
    'uploaded_at': '2026-09-18T11:35:01+00:00',
    'uploaded_via': 'api',
    'sent_to_processor': None,
}


def upload_response():
    return {'status': 200, 'body': {'data': UPLOAD_BODY}}


def test_upload_sends_multipart_with_bracketed_fields():
    client, mock = fake_client([upload_response()])
    client.documents.upload(
        '000010',
        'RetrievalRequest',
        [('receipt.pdf', b'%PDF-1.4 receipt')],
        chargeback_transaction_info_id='8675309',
    )
    kwargs = mock.request.call_args.kwargs
    assert mock.request.call_args.args[0] == 'POST'
    assert mock.request.call_args.args[1].endswith('document/upload')
    assert 'json' not in kwargs
    assert kwargs['data'] == [
        ('data[sid]', '000010'),
        ('data[doc_type]', 'RetrievalRequest'),
        ('data[chargeback_transaction_info_id]', '8675309'),
    ]
    assert kwargs['files'] == [('files[]', ('receipt.pdf', b'%PDF-1.4 receipt', 'application/pdf'))]
    assert kwargs['headers'] == {'Content-Type': None}


def test_upload_omits_chargeback_reference_when_not_given():
    client, mock = fake_client([upload_response()])
    client.documents.upload('000010', 'Underwriting', [('licence.png', b'png')])
    assert mock.request.call_args.kwargs['data'] == [
        ('data[sid]', '000010'),
        ('data[doc_type]', 'Underwriting'),
    ]


def test_upload_reads_paths_and_file_objects(tmp_path):
    path = tmp_path / 'statement.pdf'
    path.write_bytes(b'from disk')
    client, mock = fake_client([upload_response()])
    client.documents.upload('000010', 'Underwriting', [
        str(path),
        path,
        ('scan.jpg', io.BytesIO(b'from memory')),
    ])
    assert mock.request.call_args.kwargs['files'] == [
        ('files[]', ('statement.pdf', b'from disk', 'application/pdf')),
        ('files[]', ('statement.pdf', b'from disk', 'application/pdf')),
        ('files[]', ('scan.jpg', b'from memory', 'image/jpeg')),
    ]


def test_upload_maps_stored_and_failed_files():
    client, _ = fake_client([upload_response()])
    result = client.documents.upload('000010', 'RetrievalRequest', [('receipt.pdf', b'x'), ('statement.pdf', b'y')])
    assert result.message == '1 document uploaded. 1 could not be stored.'
    assert result.documents[0].uuid == '9b1c-uuid'
    assert result.documents[0].size == 20841
    assert result.failed[0].file_name == 'statement.pdf'


def test_upload_resends_whole_files_on_retry():
    client, mock = fake_client([
        {'status': 503, 'body': {}},
        upload_response(),
    ])
    client.documents.upload('000010', 'Underwriting', [('scan.jpg', io.BytesIO(b'whole file'))])
    first, second = mock.request.call_args_list
    assert first.kwargs['files'] == second.kwargs['files'] == [('files[]', ('scan.jpg', b'whole file', 'image/jpeg'))]


def test_list_maps_documents():
    client, mock = fake_client([{'status': 200, 'body': {'data': [DOCUMENT_BODY]}}])
    documents = client.documents.list('000010', {'doc_type': 'RetrievalRequest'})
    assert documents[0].chargeback_transaction_info_id == '8675309'
    assert documents[0].uploaded_via == 'api'
    assert documents[0].sent_to_processor_at is None
    assert sent_body(mock) == {'data': {'sid': '000010'}, 'filters': {'doc_type': 'RetrievalRequest'}}
    assert mock.request.call_args.args[0] == 'GET'
    assert mock.request.call_args.args[1].endswith('document/list')


def test_list_splits_sent_to_processor_pair():
    forwarded = DOCUMENT_BODY | {'sent_to_processor': ['2026-09-19 10:00:00', '00']}
    client, _ = fake_client([{'status': 200, 'body': {'data': [forwarded]}}])
    document = client.documents.list('000010')[0]
    assert document.sent_to_processor_at == '2026-09-19 10:00:00'
    assert document.processor_status == '00'


def test_list_returns_empty_list_when_none():
    client, _ = fake_client([{'status': 200, 'body': {'data': []}}])
    assert client.documents.list('000010') == []


def test_upload_wire_format_is_multipart_on_a_real_session(monkeypatch):
    import requests
    from dime_payments import Client
    from tests.helpers import make_mock_response

    sent = []

    def fake_send(session, prepared, **kwargs):
        sent.append(prepared)
        return make_mock_response(200, {'data': UPLOAD_BODY})

    monkeypatch.setattr(requests.Session, 'send', fake_send)

    Client('test-token').documents.upload('000010', 'RetrievalRequest', [('receipt.pdf', b'%PDF')])

    prepared = sent[0]
    assert prepared.headers['Content-Type'].startswith('multipart/form-data; boundary=')
    assert prepared.headers['Authorization'] == 'Bearer test-token'
    assert prepared.headers['X-Dime-Sdk'].startswith('dime-python-sdk/')
    assert b'name="data[sid]"\r\n\r\n000010' in prepared.body
    assert b'name="files[]"; filename="receipt.pdf"' in prepared.body
    assert b'Content-Type: application/pdf' in prepared.body
