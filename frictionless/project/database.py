from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from functools import cached_property
from ..schema import Schema
from ..platform import platform
from .interfaces import IFile, IFileRecord, ITable, IQueryData

if TYPE_CHECKING:
    from sqlalchemy import Table
    from ..resource import Resource


# TODO: rename to "_index" or "_files"
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
                sa.Column("type", sa.Text),
                sa.Column("updated", sa.DateTime),
                sa.Column("tableName", sa.Text, unique=True, nullable=True),
                sa.Column("resource", sa.Text),
                sa.Column("report", sa.Text),
            )
            index.create(self.connection)
        return index

    # General

    def query(self, query: str) -> IQueryData:
        sa = platform.sqlalchemy
        result = self.connection.execute(sa.text(query))
        rows = [row._asdict() for row in result]
        header = list(result.keys())
        return IQueryData(header=header, rows=rows)

    def query_table(self, query: str) -> ITable:
        result = self.query(query)
        schema = Schema.describe(result["rows"]).to_descriptor()
        return ITable(tableSchema=schema, header=result["header"], rows=result["rows"])

    # File

    def create_file(self, resource: Resource, *, on_progress=None) -> IFile:
        with resource, self.connection.begin():
            assert resource.path
            assert resource.name
            report = None
            table = None

            # Table
            if resource.type == "table":
                buffer = []

                # Get table name
                found = False
                table_names = []
                table_name = resource.name
                template = f"{table_name}%s"
                items = self.list_files()
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
            self.connection.execute(self.index.delete(self.index.c.path == resource.path))
            self.connection.execute(
                self.index.insert().values(
                    path=resource.path,
                    type=resource.type,
                    tableName=table.name if table is not None else None,
                    updated=datetime.now(),
                    resource=resource.to_json(),
                    report=report.to_json() if report is not None else "{}",
                )
            )

            # Return file
            file = self.read_file(resource.path)
            assert file
            return file

    def delete_file(self, path: str) -> str:
        file = self.read_file(path)
        assert file
        with self.connection.begin():
            if file["tableName"]:
                table = self.metadata.tables.get(file["tableName"])
                if table:
                    table.drop(self.connection)
            self.connection.execute(self.index.delete(self.index.c.path == path))
        return path

    def list_files(self) -> List[IFileRecord]:
        result = self.connection.execute(
            self.index.select().with_only_columns(
                [
                    self.index.c.path,
                    self.index.c.type,
                    self.index.c.updated,
                    self.index.c.tableName,
                ]
            )
        )
        records: List[IFileRecord] = []
        for row in result:
            file = IFileRecord(
                path=row["path"],
                type=row["type"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
            )
            records.append(file)
        return records

    def move_file(self, source: str, target: str) -> str:
        self.connection.execute(
            self.index.update(self.index.c.path == source).values(path=target)
        )
        return target

    def read_file(self, path: str) -> Optional[IFile]:
        query = self.index.select(self.index.c.path == path)
        row = self.connection.execute(query).first()
        if row:
            return IFile(
                path=row["path"],
                type=row["type"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
                resource=json.loads(row["resource"]),
                report=json.loads(row["report"]),
            )

    # TODO: rewrite
    def read_file_table(
        self,
        path: str,
        *,
        valid: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ITable:
        file = self.read_file(path)
        assert file
        query = 'select * from "%s"' % file["tableName"]
        if valid is not None:
            query = "%s where _rowValid = %s" % (query, valid)
        if limit:
            query = "%s limit %s" % (query, limit)
            if offset:
                query = "%s offset %s" % (query, offset)
        data = self.query(query)
        schema = file["resource"]["schema"]
        return ITable(tableSchema=schema, header=data["header"], rows=data["rows"])

    # TODO: implement
    def update_file(self, path: str):
        pass
