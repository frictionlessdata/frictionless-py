from __future__ import annotations
from ...exception import FrictionlessException
from .control import BigqueryControl
from ...resource import Parser
from .storage import BigqueryStorage


class BigqueryParser(Parser):
    """Bigquery parser implementation."""

    supported_types = [
        "string",
        "number",
    ]

    # Read

    def read_cell_stream_create(self):
        control = BigqueryControl.from_dialect(self.resource.dialect)
        storage = BigqueryStorage(self.resource.normdata, control=control)
        resource = storage.read_resource(control.table)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.cell_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, source):
        control = BigqueryControl.from_dialect(self.resource.dialect)
        storage = BigqueryStorage(self.resource.normdata, control=control)
        if not control.table:
            note = 'Please provide "dialect.table" for writing'
            raise FrictionlessException(note)
        source.name = control.table
        storage.write_resource(source, force=True)
