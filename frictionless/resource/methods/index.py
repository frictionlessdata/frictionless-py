from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


def index(
    self: Resource,
    database_url: str,
    *,
    table_name: Optional[str] = None,
    fast: bool = False,
    qsv: Optional[str] = None,
    on_progress: Optional[Callable[[str], None]] = None,
    use_fallback: bool = False,
    with_metadata: bool = False,
):
    """Index resource into a database"""
    Database = platform.frictionless.Database
    SqlIndexer = platform.frictionless_formats.sql.SqlIndexer

    # Metadata mode
    if with_metadata:
        assert not table_name, "Table name is not supported with metadata"
        database = Database(database_url)
        database.create_record(self, on_progress=on_progress)

    # Indexer mode
    else:
        Indexer = SqlIndexer.select_Indexer(database_url, fast=fast)
        indexer = Indexer(
            resource=self,
            database_url=database_url,
            table_name=table_name,
            qsv=qsv,
            on_progress=on_progress,
            use_fallback=use_fallback,
        )
        indexer.index()
