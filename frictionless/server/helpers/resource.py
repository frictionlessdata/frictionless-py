from __future__ import annotations

from typing import TYPE_CHECKING

from ...indexer import Indexer
from ...resources import TableResource

if TYPE_CHECKING:
    from ...resource import Resource
    from ..project import Project


def index_resource(project: Project, resource: Resource, table_name: str):
    db = project.database

    # Tabular resource
    report = None
    if isinstance(resource, TableResource):
        indexer = Indexer(
            resource=resource,
            database=db.engine,
            table_name=table_name,
            with_metadata=True,
        )
        report = indexer.index()

    # General resource
    if not report:
        report = resource.validate()

    return report
