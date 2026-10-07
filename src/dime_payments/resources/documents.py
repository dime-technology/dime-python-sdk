from __future__ import annotations

import builtins
import mimetypes
import os
from typing import IO, Any

from ..data_objects.document import Document
from ..data_objects.document_upload_result import DocumentUploadResult
from .abstract_resource import AbstractResource

# A path to read, or a (filename, content) pair where content is bytes or a
# binary file object.
DocumentFile = str | os.PathLike[str] | tuple[str, bytes | IO[bytes]]


class Documents(AbstractResource):
    """
    Document endpoints. Uploading requires ``document:create``; listing requires
    ``document:read``.
    """

    def upload(
        self,
        sid: str,
        doc_type: str,
        files: builtins.list[DocumentFile],
        chargeback_transaction_info_id: str | None = None,
    ) -> DocumentUploadResult:
        """
        Send documents for a merchant.

        ``doc_type`` is one of ``Verification``, ``FraudHolds``, ``Underwriting``
        or ``RetrievalRequest`` — use ``RetrievalRequest`` for chargeback
        evidence, and pass ``chargeback_transaction_info_id`` to attach it to
        that dispute.

        Each entry in ``files`` is a path, or a ``(filename, content)`` pair
        whose content is bytes or a binary file object. Up to 10 files, each
        9 MB or smaller, as PDF, JPG, PNG, DOC, DOCX or RTF. Files are read
        before sending, so a retried request re-sends them whole.

        Files are stored independently: check :attr:`DocumentUploadResult.failed`
        and re-send only those. Uploading does not forward anything to the
        processor; Dime reviews the documents and forwards them.
        """
        body = self._envelope({
            'sid': sid,
            'doc_type': doc_type,
            'chargeback_transaction_info_id': chargeback_transaction_info_id,
        })
        parts = [('files[]', self._file_part(file)) for file in files]
        raw = self._transport.request('POST', 'document/upload', body, files=parts)
        return DocumentUploadResult.from_dict(raw.get('data') or {})

    def list(self, sid: str, filters: dict[str, Any] | None = None) -> builtins.list[Document]:
        """
        List the documents held for a merchant, however they arrived.

        ``filters`` takes ``doc_type`` and ``chargeback_transaction_info_id``.
        A merchant with no documents returns an empty list, not an error.
        """
        body = self._envelope({'sid': sid}, filters or {})
        raw = self._transport.request('GET', 'document/list', body)
        documents = raw.get('data', [])
        if isinstance(documents, dict):
            documents = list(documents.values())
        return [Document.from_dict(document) for document in documents if isinstance(document, dict)]

    @staticmethod
    def _file_part(file: DocumentFile) -> tuple[str, bytes, str]:
        if isinstance(file, tuple):
            filename, content = file
            data = content if isinstance(content, bytes) else content.read()
        else:
            filename = os.path.basename(os.fspath(file))
            with open(file, 'rb') as handle:
                data = handle.read()

        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        return filename, data, content_type
