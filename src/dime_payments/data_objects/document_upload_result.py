from dataclasses import dataclass, field
from typing import Any

from ..support.arr import arr_array, arr_string
from .document import Document


@dataclass
class DocumentUploadFailure:
    """A file from an upload that could not be stored. Re-send just this one."""

    file_name: str | None = None
    reason: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DocumentUploadFailure':
        return cls(
            file_name=arr_string(data, 'file_name'),
            reason=arr_string(data, 'reason'),
        )


@dataclass
class DocumentUploadResult:
    """
    The outcome of :meth:`Documents.upload`.

    Files are stored independently, so an upload can partly succeed: ``documents``
    lists what was stored and ``failed`` what was not.
    """

    message: str | None = None
    documents: list[Document] = field(default_factory=list)
    failed: list[DocumentUploadFailure] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DocumentUploadResult':
        return cls(
            message=arr_string(data, 'message'),
            documents=[Document.from_dict(d) for d in arr_array(data, 'documents') if isinstance(d, dict)],
            failed=[DocumentUploadFailure.from_dict(f) for f in arr_array(data, 'failed') if isinstance(f, dict)],
        )
