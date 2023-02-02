from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from functools import cached_property
from ..schema import Schema
from ..platform import platform
from .interfaces import IRecord, IListedRecord, ITable

if TYPE_CHECKING:
    from sqlalchemy import Table
    from ..resource import Resource


TABLE_NAME_RESOURCES = "_resources"
BUFFER_SIZE = 1000


class Database:
    database_url: str

    def __init__(self, database_url: str):
        self.database_url = database_url

    @cached_property
    def engine(self):
        return platform.sqlalchemy.create_engine(self.database_url)

    @cached_property
    def connection(self):
        return self.engine.connect()

    @cached_property
    def metadata(self):
        metadata = platform.sqlalchemy.MetaData()
        metadata.reflect(self.connection)
        return metadata

    @cached_property
    def mapper(self):
        # TODO: pass database_url
        return platform.frictionless_formats.sql.SqlMapper(self.engine)

    @cached_property
    def index(self) -> Table:
        sa = platform.sqlalchemy
        index = self.metadata.tables.get(TABLE_NAME_RESOURCES)
        if index is None:
            index = sa.Table(
                TABLE_NAME_RESOURCES,
                self.metadata,
                sa.Column("path", sa.Text, primary_key=True),
                sa.Column("updated", sa.DateTime),
                sa.Column("tableName", sa.Text, unique=True),
                sa.Column("resource", sa.Text),
                sa.Column("report", sa.Text),
            )
            index.create(self.connection)
        return index

    # Resources

    def create_resource(self, resource: Resource, *, on_progress=None) -> IRecord:
        with resource, self.connection.begin():
            assert resource.path
            assert resource.name
            buffer = []

            # Get table name
            found = False
            table_names = []
            table_name = resource.name
            template = f"{table_name}%s"
            items = self.list_resources()
            for item in items:
                table_names.append(item["tableName"])
                if item["path"] == resource.path:
                    table_name = item["tableName"]
                    found = True
            if not found:
                suffix = 1
                while table_name in table_names:
                    table_name = template % suffix
                    suffix += 1

            # Remove existing table
            existing_table = self.metadata.tables.get(table_name)
            if existing_table is not None:
                existing_table.drop(self.connection)
                self.metadata.remove(existing_table)

            # Create new table
            table = self.mapper.write_schema(
                resource.schema,
                table_name=table_name,
                with_metadata=True,
            )
            table.to_metadata(self.metadata)
            table.create(self.connection)

            # Write row
            def on_row(row):
                cells = self.mapper.write_row(row)
                cells = [row.row_number, row.valid] + cells
                buffer.append(cells)
                if len(buffer) > BUFFER_SIZE:
                    self.connection.execute(table.insert().values(buffer))
                    buffer.clear()
                if on_progress:
                    on_progress(f"{resource.stats.rows} rows")

            # Validate/iterate
            report = resource.validate(on_row=on_row)
            if len(buffer):
                self.connection.execute(table.insert().values(buffer))

            # Register resource
            self.connection.execute(self.index.delete(self.index.c.path == resource.path))
            self.connection.execute(
                self.index.insert().values(
                    path=resource.path,
                    tableName=table.name,
                    updated=datetime.now(),
                    resource=resource.to_json(),
                    report=report.to_json(),
                )
            )

            # Return resource item
            record = self.read_resource(resource.path)
            assert record
            return record

    # TODO: remove table
    def delete_resource(self, path: str) -> str:
        with self.connection.begin():
            self.connection.execute(self.index.delete(self.index.c.path == path))
        return path

    def list_resources(self) -> List[IListedRecord]:
        columns = [self.index.c.path, self.index.c.updated, self.index.c.tableName]
        result = self.connection.execute(self.index.select().with_only_columns(columns))
        records: List[IListedRecord] = []
        for row in result:
            record = IListedRecord(
                path=row["path"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
            )
            records.append(record)
        return records

    def query_resources(self, query: str) -> ITable:
        sa = platform.sqlalchemy
        result = self.connection.execute(sa.text(query))
        rows = [row._asdict() for row in result]
        header = list(result.keys())
        schema = Schema.describe(rows).to_descriptor()
        return ITable(tableSchema=schema, header=header, rows=rows)

    def read_resource(self, path: str) -> Optional[IRecord]:
        query = self.index.select(self.index.c.path == path)
        row = self.connection.execute(query).first()
        if row:
            return IRecord(
                path=row["path"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
                resource=json.loads(row["resource"]),
                report=json.loads(row["report"]),
            )

    # TODO: implement
    def update_resource(self, path: str):
        pass
