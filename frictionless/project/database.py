from __future__ import annotations
import json
from typing import TYPE_CHECKING
from datetime import datetime
from functools import cached_property
from ..platform import platform

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
                sa.Column("table_name", sa.Text, unique=True),
                sa.Column("updated", sa.DateTime),
                sa.Column("resource", sa.Text),
                sa.Column("report", sa.Text),
            )
            index.create(self.connection)
        return index

    # Query

    def query(self, query: str):
        sa = platform.sqlalchemy
        result = self.connection.execute(sa.text(query)).mappings()
        return list(result)

    # Resources

    def list_resources(self):
        return list(
            self.connection.execute(
                self.index.select().with_only_columns(
                    [
                        self.index.c.path,
                        self.index.c.table_name,
                        self.index.c.updated,
                    ]
                )
            ).mappings()
        )

    def create_resource(self, resource: Resource, *, on_progress=None):
        with resource, self.connection.begin():
            assert resource.path
            assert resource.name
            buffer = []

            # Get table name
            found = False
            table_names = []
            table_name = resource.name
            template = f"{table_name}%s"
            records = self.list_resources()
            for record in records:
                table_names.append(record.table_name)
                if record.path == resource.path:
                    table_name = record.table_name
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
                table_name=table_name,  # type: ignore
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
            self.connection.execute(
                self.index.delete(self.index.c.table_name == table.name)
            )
            return self.connection.execute(
                self.index.insert().values(
                    path=resource.path,
                    table_name=table.name,
                    updated=datetime.now(),
                    resource=resource.to_json(),
                    report=report.to_json(),
                )
            ).mappings()

    def read_resource(self, path: str):
        query = self.index.select(self.index.c.path == path)
        record = self.connection.execute(query).mappings().first()
        if record:
            record = dict(record)
            record["resource"] = json.loads(record["resource"])
            record["report"] = json.loads(record["report"])
            return record

    # TODO: remove table
    def delete_resource(self, path: str):
        with self.connection.begin():
            self.connection.execute(self.index.delete(self.index.c.path == path))
