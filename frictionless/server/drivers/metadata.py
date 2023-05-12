from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tinydb import TinyDB
from tinydb.table import Table, Document

if TYPE_CHECKING:
    from ..project import Project


class Metadata:
    resources: Table

    def __init__(self, project: Project):
        fullpath = project.private / "metadata.json"
        database = TinyDB(fullpath, indent=2)
        self.resources = MetadataTable(database.storage, name="resources")

    def document(self, doc_id: str, **props: Any):
        return Document(props, doc_id=doc_id)  # type: ignore


# Internal


class MetadataTable(Table):
    document_id_class = str

    def _get_next_id(self):
        raise RuntimeError("id must be provided")
