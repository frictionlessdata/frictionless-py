from __future__ import annotations
from typing import TYPE_CHECKING
from ...exception import FrictionlessException
from ...system import Parser
from .control import SqlControl
from .adapter import SqlAdapter

if TYPE_CHECKING:
    from ...resource import Resource


class SqlParser(Parser):
    """SQL parser implementation."""

    supported_types = [
        "boolean",
        "date",
        "datetime",
        "integer",
        "number",
        "string",
        "time",
    ]

    # Read

    def read_cell_stream_create(self):
        control = SqlControl.from_dialect(self.resource.dialect)
        if not control.table:
            raise FrictionlessException('Please provide "dialect.sql.table" for reading')
        adapter = SqlAdapter.from_source(self.resource.normpath)
        if not adapter:
            raise FrictionlessException(f"Not supported source: {self.resource.normpath}")
        if not self.resource.has_schema:
            self.resource.schema = adapter.read_schema(control.table)
        return adapter.read_cell_stream(control)

    # Write

    def write_row_stream(self, source: Resource):
        control = SqlControl.from_dialect(self.resource.dialect)
        if not control.table:
            raise FrictionlessException('Please provide "dialect.sql.table" for writing')
        adapter = SqlAdapter.from_source(self.resource.normpath)
        if not adapter:
            raise FrictionlessException(f"Not supported source: {self.resource.normpath}")
        with source:
            adapter.write_schema(source.schema, table_name=control.table)
            adapter.write_row_stream(source.row_stream, table_name=control.table)
