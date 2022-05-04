from ...exception import FrictionlessException
from ...parser import Parser
from .storage import SqlStorage
from ... import errors


class SqlParser(Parser):
    """SQL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlParser`

    """

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

    def read_list_stream_create(self):
        dialect = self.resource.dialect
        storage = SqlStorage(self.resource.fullpath, dialect=dialect)
        resource = storage.read_resource(
            dialect.table, order_by=dialect.order_by, where=dialect.where
        )
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        if not target.dialect.table:
            note = 'Please provide "dialect.table" for writing'
            raise FrictionlessException(errors.StorageError(note=note))
        source.name = target.dialect.table
        storage = SqlStorage(target.fullpath, dialect=target.dialect)
        storage.write_resource(source, force=True)
