from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, List, Optional

from tinydb import TinyDB
from tinydb.queries import QueryInstance
from tinydb.table import Document

from ... import types
from .. import helpers

if TYPE_CHECKING:
    from ..project import Project


class Metadata:
    database: TinyDB
    tables: Dict[str, helpers.StringIndexedTable]

    def __init__(self, project: Project):
        fullpath = project.private / "metadata.json"
        self.database = TinyDB(fullpath, indent=2)
        self.tables = {}

    # Documents

    def delete_document(self, *, name: str, type: str) -> List[int]:
        table = self.get_table(type)
        return table.remove(doc_ids=[name])  # type: ignore

    def iter_documents(self, *, type: str) -> Iterator[types.IDescriptor]:
        table = self.get_table(type)
        yield from table

    def find_document(
        self, *, type: str, query: QueryInstance
    ) -> Optional[types.IDescriptor]:
        table = self.get_table(type)
        return table.get(query)  # type: ignore

    def read_document(self, *, name: str, type: str) -> Optional[types.IDescriptor]:
        table = self.get_table(type)
        return table.get(doc_id=name)  # type: ignore

    def write_document(
        self, *, name: str, type: str, descriptor: types.IDescriptor
    ) -> None:
        table = self.get_table(type)
        table.upsert(Document(descriptor, doc_id=name))  # type: ignore

    # Tables

    def get_table(self, type: str) -> helpers.StringIndexedTable:
        return self.tables.setdefault(
            type, helpers.StringIndexedTable(self.database.storage, name=type)
        )
