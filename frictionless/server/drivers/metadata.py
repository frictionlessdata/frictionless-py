from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tinydb import TinyDB
from tinydb.table import Table, Document
from .. import helpers

if TYPE_CHECKING:
    from ..project import Project


class Metadata:
    resources: Table

    def __init__(self, project: Project):
        fullpath = project.private / "metadata.json"
        database = TinyDB(fullpath, indent=2)
        self.resources = helpers.StringIndexedTable(database.storage, name="resources")

    def document(self, doc_id: str, **props: Any):
        return Document(props, doc_id=doc_id)  # type: ignore
