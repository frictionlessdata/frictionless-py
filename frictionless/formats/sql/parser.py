from __future__ import annotations
from ...exception import FrictionlessException
from ...resource import Parser
from .storage import SqlStorage
from .control import SqlControl


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
        assert isinstance(control, SqlControl)
        if not control.table:
            note = 'Please provide "dialect.sql.table" for reading'
            raise FrictionlessException(note)
        storage = SqlStorage(self.resource.normpath, control=control)
        resource = storage.read_resource(
            control.table, order_by=control.order_by, where=control.where
        )
        self.resource.schema = resource.schema
        with resource:
            yield from resource.cell_stream  # type: ignore

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, source):
        control = SqlControl.from_dialect(self.resource.dialect)
        if not control.table:
            note = 'Please provide "dialect.sql.table" for writing'
            raise FrictionlessException(note)
        source.name = control.table
        storage = SqlStorage(self.resource.normpath, control=control)
        storage.write_resource(source, force=True)
