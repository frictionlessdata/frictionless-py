from __future__ import annotations
import builtins
from typing import TYPE_CHECKING, Optional
from ..platform import platform
from ..resource import Resource

if TYPE_CHECKING:
    from ..formats.sql import IOnRow, IOnProgress
    from ..interfaces import IFilterFunction, IProcessFunction, IExtractedRows


class TableResource(Resource):
    type = "table"
    datatype = "table"
    tabular = True

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> IExtractedRows:
        if not process:
            process = lambda row: row.to_dict()
        data = self.read_rows(size=limit_rows)
        data = builtins.filter(filter, data) if filter else data
        data = (process(row) for row in data) if process else data
        return {name or self.name: list(data)}

    # Index

    def index(
        self,
        database_url: str,
        *,
        table_name: str,
        fast: bool = False,
        qsv_path: Optional[str] = None,
        on_row: Optional[IOnRow] = None,
        on_progress: Optional[IOnProgress] = None,
        use_fallback: bool = False,
    ) -> None:
        """Index resource into a database"""
        indexer = platform.frictionless_formats.sql.SqlIndexer(
            resource=self,
            database_url=database_url,
            table_name=table_name,
            fast=fast,
            qsv_path=qsv_path,
            on_row=on_row,
            on_progress=on_progress,
            use_fallback=use_fallback,
        )
        indexer.index()
