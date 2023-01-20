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
    qsv_path: Optional[str] = None,
    on_progress: Optional[Callable[[str], None]] = None,
    use_fallback: bool = False,
    with_metadata: bool = False,
):
    """Index resource into a database"""

    # Metadata mode
    if with_metadata:
        assert not table_name, "Table name is prohibited in metadata mode"
        database = platform.frictionless.Database(database_url)
        database.create_resource(self, on_progress=on_progress)

    # Normal mode
    else:
        assert table_name, "Table name is required in normal mode"
        indexer = platform.frictionless_formats.sql.SqlIndexer(
            resource=self,
            database_url=database_url,
            table_name=table_name,
            fast=fast,
            qsv_path=qsv_path,
            on_progress=on_progress,
            use_fallback=use_fallback,
        )
        indexer.index()
