from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Any
from tinydb import TinyDB
from tinydb.table import Table, Document
from .. import helpers

if TYPE_CHECKING:
    from ..project import Project


class Artifact:
    facts: Table
    reports: Path

    def __init__(self, project: Project):
        basepath = project.private / "artifact"

        # General
        fullpath = basepath / "artifact.json"
        database = TinyDB(fullpath, indent=2)
        self.facts = helpers.StringIndexedTable(database.storage, name="facts")

        # Reports
        self.reports = basepath / "reports"
        if not self.reports.is_dir():
            self.reports.mkdir(parents=True)

    def document(self, doc_id: str, **props: Any):
        return Document(props, doc_id=doc_id)  # type: ignore
