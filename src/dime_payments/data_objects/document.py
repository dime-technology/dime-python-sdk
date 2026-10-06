from dataclasses import dataclass
from typing import Any

from ..support.arr import arr_int, arr_string


@dataclass
class Document:
    """
    A document held for a merchant.

    ``doc_type`` is one of ``Verification``, ``FraudHolds``, ``Underwriting`` or
    ``RetrievalRequest``. ``uploaded_via`` is ``api`` for documents sent through
    :meth:`Documents.upload`. The upload response carries only ``uuid``,
    ``file_name``, ``doc_type`` and ``size``; the rest are filled by
    :meth:`Documents.list`.

    ``sent_to_processor_at`` and ``processor_status`` record when our team
    forwarded the document to the processor and what it answered. Both are
    ``None`` until it has been forwarded.
    """

    uuid: str | None = None
    file_name: str | None = None
    doc_type: str | None = None
    chargeback_transaction_info_id: str | None = None
    size: int | None = None
    uploaded_at: str | None = None
    uploaded_via: str | None = None
    sent_to_processor_at: str | None = None
    processor_status: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Document':
        # The API reports forwarding as a [timestamp, processor status] pair.
        sent = data.get('sent_to_processor')
        pair = dict(zip(('at', 'status'), sent)) if isinstance(sent, list) else {'at': sent}

        return cls(
            uuid=arr_string(data, 'uuid'),
            file_name=arr_string(data, 'file_name'),
            doc_type=arr_string(data, 'doc_type'),
            chargeback_transaction_info_id=arr_string(data, 'chargeback_transaction_info_id'),
            size=arr_int(data, 'size'),
            uploaded_at=arr_string(data, 'uploaded_at'),
            uploaded_via=arr_string(data, 'uploaded_via'),
            sent_to_processor_at=arr_string(pair, 'at'),
            processor_status=arr_string(pair, 'status'),
        )
