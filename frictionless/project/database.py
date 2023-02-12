from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from functools import cached_property
from ..schema import Schema
from ..platform import platform
from .interfaces import IRecord, IRecordItem, ITable, IQueryData, IFieldItem

if TYPE_CHECKING:
    from sqlalchemy import Table
    from ..resource import Resource


PROJECT_IDENTIFIER = "_project"
RECORDS_IDENTIFIER = "_records"
BUFFER_SIZE = 1000


class Database:
    database_url: str
    project: Table
    records: Table

    def __init__(self, database_url: str):
        sa = platform.sqlalchemy
        self.database_url = database_url

        # Ensure project table
        self.project = self.metadata.tables.get(PROJECT_IDENTIFIER)
        if self.project is None:
            self.project = sa.Table(
                PROJECT_IDENTIFIER,
                self.metadata,
                sa.Column("config", sa.Text),
            )
            self.project.create(self.connection)

        # Ensure records table
        # TODO: move some columns to metadata/other-name json column to avoid migrations
        self.records = self.metadata.tables.get(RECORDS_IDENTIFIER)
        if self.records is None:
            self.records = sa.Table(
                RECORDS_IDENTIFIER,
                self.metadata,
                sa.Column("path", sa.Text, primary_key=True),
                sa.Column("type", sa.Text),
                sa.Column("updated", sa.DateTime),
                sa.Column("tableName", sa.Text, unique=True, nullable=True),
                sa.Column("resource", sa.Text),
                sa.Column("report", sa.Text),
            )
            self.records.create(self.connection)

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

    # General

    def query(self, query: str) -> IQueryData:
        sa = platform.sqlalchemy
        result = self.connection.execute(sa.text(query))
        rows = [row._asdict() for row in result]
        header = list(result.keys())
        return IQueryData(header=header, rows=rows)

    # Field

    def list_fields(self) -> List[IFieldItem]:
        sa = platform.sqlalchemy
        items: List[IFieldItem] = []
        # TODO: write properly
        result = self.connection.execute(
            sa.text(
                "SELECT path, tableName, json_extract(resource, '$.schema') as schema FROM _records WHERE type = 'table' ORDER BY tableName"
            )
        )
        for row in result:
            schema = Schema.from_descriptor(json.loads(row["schema"]))
            for field in schema.fields:
                items.append(
                    IFieldItem(
                        # TODO: review why it's not required
                        name=field.name,  # type: ignore
                        type=field.type,
                        tableName=row["tableName"],
                        tablePath=row["path"],
                    )
                )

        return items

    # Record

    def create_record(self, resource: Resource, *, on_progress=None) -> IRecord:
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
                items = self.list_records()
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
            self.connection.execute(
                self.records.delete(self.records.c.path == resource.path)
            )
            self.connection.execute(
                self.records.insert().values(
                    path=resource.path,
                    type=resource.type,
                    tableName=table.name if table is not None else None,
                    updated=datetime.now(),
                    resource=resource.to_json(),
                    report=report.to_json() if report is not None else "{}",
                )
            )

            # Return record
            record = self.read_record(resource.path)
            assert record
            return record

    def delete_record(self, path: str) -> Optional[IRecord]:
        record = self.read_record(path)
        if record:
            with self.connection.begin():
                if record["tableName"]:
                    table = self.metadata.tables.get(record["tableName"])
                    if table is not None:
                        table.drop(self.connection)
                self.connection.execute(self.records.delete(self.records.c.path == path))
            return record

    def list_records(self) -> List[IRecordItem]:
        result = self.connection.execute(
            self.records.select().with_only_columns(
                [
                    self.records.c.path,
                    self.records.c.type,
                    self.records.c.updated,
                    self.records.c.tableName,
                ]
            )
        )
        items: List[IRecordItem] = []
        for row in result:
            item = IRecordItem(
                path=row["path"],
                type=row["type"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
            )
            items.append(item)
        return items

    def move_record(self, source: str, target: str) -> str:
        self.connection.execute(
            self.records.update(self.records.c.path == source).values(path=target)
        )
        return target

    def read_record(self, path: str) -> Optional[IRecord]:
        query = self.records.select(self.records.c.path == path)
        row = self.connection.execute(query).first()
        if row:
            return IRecord(
                path=row["path"],
                type=row["type"],
                updated=row["updated"].isoformat(),
                tableName=row["tableName"],
                resource=json.loads(row["resource"]),
                report=json.loads(row["report"]),
            )

    # TODO: implement
    def update_record(self, path: str):
        pass

    # Table

    def query_table(self, query: str) -> ITable:
        result = self.query(query)
        schema = Schema.describe(result["rows"]).to_descriptor()
        return ITable(tableSchema=schema, header=result["header"], rows=result["rows"])

    # TODO: rewrite
    def read_table(
        self,
        path: str,
        *,
        valid: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ITable:
        record = self.read_record(path)
        assert record
        assert "tableName" in record
        query = 'select * from "%s"' % record["tableName"]
        if valid is not None:
            query = "%s where _rowValid = %s" % (query, valid)
        if limit:
            query = "%s limit %s" % (query, limit)
            if offset:
                query = "%s offset %s" % (query, offset)
        data = self.query(query)
        schema = record["resource"]["schema"]
        return ITable(tableSchema=schema, header=data["header"], rows=data["rows"])
