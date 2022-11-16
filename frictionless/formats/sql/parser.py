from __future__ import annotations
from sys import platform
from typing import TYPE_CHECKING
from ...exception import FrictionlessException
from ...resource import Parser
from ...platform import platform
from .control import SqlControl
from .manager import SqlManager

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
        sa = platform.sqlalchemy
        control = SqlControl.from_dialect(self.resource.dialect)
        if not control.table:
            note = 'Please provide "dialect.sql.table" for reading'
            raise FrictionlessException(note)
        manager = SqlManager(control, database_url=self.resource.normpath)
        table = manager.metadata.tables.get(control.table)
        self.resource.schema = manager.mapper.to_schema(table)
        with manager.connection.begin():
            # Streaming could be not working for some backends:
            # http://docs.sqlalchemy.org/en/latest/core/connections.html
            select = table.select().execution_options(stream_results=True)
            if control.order_by:
                select = select.order_by(sa.sql.text(control.order_by))
            if control.where:
                select = select.where(sa.sql.text(control.where))
            result = select.execute()
            yield list(result.keys())
            for item in result:
                cells = list(item)
                yield cells

    # Write

    # TODO: rebase on copy (when possible)?
    def write_row_stream(self, source: Resource):
        control = SqlControl.from_dialect(self.resource.dialect)
        if not control.table:
            note = 'Please provide "dialect.sql.table" for writing'
            raise FrictionlessException(note)
        manager = SqlManager(control, database_url=self.resource.normpath)
        buffer = []
        buffer_size = 1000
        with source:
            table = manager.mapper.from_schema(
                source.schema,
                engine=manager.engine,
                table_name=control.table,
            )
            manager.metadata.create_all(tables=[table])
            for row in source.row_stream:
                cells = manager.mapper.from_row(row)
                buffer.append(cells)
                if len(buffer) > buffer_size:
                    # sqlalchemy conn.execute(sql_table.insert(), buffer)
                    # syntax applies executemany DB API invocation.
                    manager.connection.execute(table.insert(), buffer)
                    buffer = []
            if len(buffer):
                manager.connection.execute(table.insert(), buffer)
