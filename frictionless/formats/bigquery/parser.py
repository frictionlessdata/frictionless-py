# type: ignore
from ...exception import FrictionlessException
from ...resource import Parser
from .storage import BigqueryStorage


class BigqueryParser(Parser):
    """Bigquery parser implementation."""

    supported_types = [
        "string",
        "number",
    ]

    # Read

    def read_list_stream_create(self):
        control = self.resource.dialect.get_control("bigquery")
        storage = BigqueryStorage(self.resource.data, control=control)
        resource = storage.read_resource(control.table)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, source):
        control = self.resource.dialect.get_control("bigquery")
        storage = BigqueryStorage(self.resource.data, control=control)
        if not control.table:
            note = 'Please provide "dialect.table" for writing'
            raise FrictionlessException(note)
        source.name = control.table
        storage.write_resource(source, force=True)
