from ...exception import FrictionlessException
from ...parser import Parser
from ... import errors
from .storage import BigqueryStorage


class BigqueryParser(Parser):
    """Bigquery parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.bigquery import BigqueryParser`
    """

    supported_types = [
        "string",
        "number",
    ]

    # Read

    def read_list_stream_create(self):
        dialect = self.resource.dialect
        storage = BigqueryStorage(self.resource.data, dialect=dialect)
        resource = storage.read_resource(dialect.table)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        storage = BigqueryStorage(self.resource.data, dialect=target.dialect)
        if not target.dialect.table:
            note = 'Please provide "dialect.table" for writing'
            raise FrictionlessException(errors.StorageError(note=note))
        source.name = target.dialect.table
        storage.write_resource(source, force=True)
