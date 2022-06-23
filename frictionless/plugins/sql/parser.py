from ...exception import FrictionlessException
from .control import SqlControl
from ...parser import Parser
from .storage import SqlStorage


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
        control = self.resource.dialect.get_control("sql", ensure=SqlControl())
        storage = SqlStorage(self.resource.fullpath, control=control)
        resource = storage.read_resource(
            control.table, order_by=control.order_by, where=control.where
        )
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        control = target.dialect.get_control("sql", ensure=SqlControl())
        if not control.table:
            note = 'Please provide "control.table" for writing'
            raise FrictionlessException(note)
        source.name = control.table
        storage = SqlStorage(target.fullpath, control=control)
        storage.write_resource(source, force=True)
