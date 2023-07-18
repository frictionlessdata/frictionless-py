from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional

from ... import models
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import Adapter
from . import settings
from .control import SqlControl
from .mapper import SqlMapper

if TYPE_CHECKING:
    from sqlalchemy import MetaData, Table
    from sqlalchemy.engine import Engine

    from ...report import Report
    from ...resources import TableResource
    from ...schema import Schema
    from ...table import IRowStream, Row


class SqlAdapter(Adapter):
    """Read and write data from/to SQL database"""

    engine: Engine
    control: SqlControl
    mapper: SqlMapper
    metadata: MetaData

    def __init__(self, engine: Engine, *, control: Optional[SqlControl] = None):
        sa = platform.sqlalchemy
        self.engine = engine
        self.control = control or SqlControl()
        self.mapper = SqlMapper(self.engine.dialect.name)
        with self.engine.begin() as conn:
            # It will fail silently if this function already exists
            if self.engine.dialect.name.startswith("sqlite"):
                conn.connection.create_function("REGEXP", 2, regexp)  # type: ignore
            self.metadata = sa.MetaData(schema=self.control.namespace)
            self.metadata.reflect(conn, views=True)

    # Delete

    def delete_resource(self, table_name: str) -> None:
        with self.engine.begin() as conn:
            table = self.metadata.tables[table_name]
            self.metadata.drop_all(conn, tables=[table])

    # Read

    def read_package(self) -> Package:
        package = Package(resources=[])
        for table in self.metadata.sorted_tables:
            name = str(table.name)
            control = SqlControl(table=name)
            path = self.engine.url.render_as_string(hide_password=False)
            schema = self.mapper.read_schema(table)
            resource = Resource(path, name=name, schema=schema, control=control)
            package.add_resource(resource)
        return package

    def read_schema(self, table_name: str) -> Schema:
        table = self.metadata.tables[table_name]
        return self.mapper.read_schema(table, with_metadata=self.control.with_metadata)

    def read_cell_stream(self, control: SqlControl) -> Generator[List[Any], None, None]:
        sa = platform.sqlalchemy
        table = self.metadata.tables[control.table]  # type: ignore
        with self.engine.begin() as conn:
            # Prepare columns
            columns = table.c
            if self.control.with_metadata:
                columns = [
                    column
                    for column in table.c
                    if column.name not in settings.METADATA_IDENTIFIERS
                ]

            # Prepare query
            # Streaming could be not working for some backends:
            # http://docs.sqlalchemy.org/en/latest/core/connections.html
            query = sa.select(*columns).execution_options(stream_results=True)
            if control.order_by:
                query = query.order_by(sa.text(control.order_by))
            if control.where:
                query = query.where(sa.text(control.where))

            # Stream cells
            result = conn.execute(query)
            yield list(result.keys())
            for item in result:
                cells = list(item)
                yield cells

    # Write

    def write_package(self, package: Package):
        with self.engine.begin() as conn:
            tables: List[Table] = []
            for res in package.resources:
                assert res.name
                table = self.mapper.write_schema(res.schema, table_name=res.name)
                table = table.to_metadata(self.metadata)
                tables.append(table)
            self.metadata.create_all(conn, tables=tables)
        for table in self.metadata.sorted_tables:
            if package.has_table_resource(table.name):
                resource = package.get_table_resource(table.name)
                with resource:
                    self.write_row_stream(resource.row_stream, table_name=table.name)
        return models.PublishResult(
            url=self.engine.url.render_as_string(hide_password=True),
            context=dict(engine=self.engine),
        )

    def write_schema(
        self,
        schema: Schema,
        *,
        table_name: str,
        force: bool = False,
        with_metadata: bool = False,
    ) -> None:
        with self.engine.begin() as conn:
            if force:
                existing_table = self.metadata.tables.get(table_name)
                if existing_table is not None:
                    self.metadata.drop_all(conn, tables=[existing_table])
                    self.metadata.remove(existing_table)
            table = self.mapper.write_schema(
                schema, table_name=table_name, with_metadata=with_metadata
            )
            table = table.to_metadata(self.metadata)
            self.metadata.create_all(conn, tables=[table])

    def write_row_stream(
        self,
        row_stream: IRowStream,
        *,
        table_name: str,
        on_row: Optional[Callable[[Row], None]] = None,
    ) -> None:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            buffer: List[Dict[str, Any]] = []
            table = self.metadata.tables[table_name]
            for row in row_stream:
                buffer.append(self.mapper.write_row(row))
                if len(buffer) > settings.BUFFER_SIZE:
                    conn.execute(sa.insert(table), buffer)
                    buffer.clear()
                on_row(row) if on_row else None
            if len(buffer):
                conn.execute(sa.insert(table), buffer)

    def write_resource_with_metadata(
        self,
        resource: TableResource,
        *,
        table_name: str,
        on_row: Optional[Callable[[Row], None]] = None,
    ) -> Report:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            # Write row
            def process_row(row: Row):
                buffer.append(self.mapper.write_row(row, with_metadata=True))
                if len(buffer) > settings.BUFFER_SIZE:
                    conn.execute(sa.insert(table), buffer)
                    buffer.clear()
                on_row(row) if on_row else None

            # Validate/iterate
            buffer: List[Dict[str, Any]] = []
            table = self.metadata.tables[table_name]
            report = resource.validate(on_row=process_row)
            if len(buffer):
                conn.execute(sa.insert(table), buffer)

            return report


# Internal


def regexp(expr: str, item: str):
    reg = re.compile(expr)
    return reg.search(item) is not None
