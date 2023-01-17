from __future__ import annotations
import attrs
import subprocess
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Callable
from ...schema import Schema, Field
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource
    from sqlalchemy import Table


BLOCK_SIZE = 8096
BUFFER_SIZE = 1000
INDEX_NAME = "_index"


def index(
    self: Resource,
    database_url: str,
    *,
    table_name: Optional[str] = None,
    fast: bool = False,
    qsv: Optional[str] = None,
    callback: Optional[Callable[[str], None]] = None,
    with_metadata: bool = False,
):
    """Index resource into a database"""

    # Prepare url
    if "://" not in database_url:
        database_url = f"sqlite:///{database_url}"
    url = platform.sqlalchemy.engine.make_url(database_url)

    # Select indexer
    Indexer = GeneralIndexer
    if fast:
        if url.drivername.startswith("sqlite"):
            Indexer = FastSqliteIndexer
        elif url.drivername.startswith("postgresql"):
            Indexer = FastPostgresIndexer

    # Run indexer
    indexer = Indexer(
        resource=self,
        database_url=database_url,
        table_name=table_name,
        qsv=qsv,
        callback=callback,
        with_metadata=with_metadata,
    )
    indexer.index()


# Internal


@attrs.define(kw_only=True)
class Indexer:

    # State

    resource: Resource
    database_url: str
    table_name: Optional[str] = None
    qsv: Optional[str] = None
    callback: Optional[Callable[[str], None]] = None
    with_metadata: Optional[bool] = False

    # Props

    @cached_property
    def mapper(self):
        # TODO: pass database_url
        return platform.frictionless_formats.sql.SqlMapper(self.engine)

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

    # Progress

    def report_progress(self, message: str):
        if self.callback:
            self.callback(message)

    # Index

    def index(self):
        self.prepare_resource()
        with self.resource:
            with self.connection.begin():
                index = self.prepare_index()
                table = self.prepare_table(index=index)
                self.index_resource(table, index=index)

    def prepare_resource(self):
        if self.qsv:
            PIPE = subprocess.PIPE
            command = [self.qsv, "stats", "--infer-dates", "--dates-whitelist", "all"]
            process = subprocess.Popen(command, stdout=PIPE, stdin=PIPE)
            with self.resource.open(as_file=True):
                while True:
                    chunk = self.resource.read_bytes(size=BLOCK_SIZE)
                    if not chunk:
                        break
                    process.stdin.write(chunk)  # type: ignore
                process.stdin.close()  # type: ignore
                result = process.stdout.read()  # type: ignore
                process.wait()
                schema = Schema()
                with platform.frictionless.Resource(result, format="csv") as info:
                    # TODO: move to formats.qsv.QsvMapper?
                    for row in info.row_stream:
                        type = "string"
                        if row["type"] == "Integer":
                            type = "integer"
                        elif row["type"] == "Float":
                            type = "number"
                        elif row["type"] == "DateTime":
                            type = "datetime"
                        elif row["type"] == "Date":
                            type = "date"
                        descriptor = {"name": row["field"], "type": type}
                        schema.add_field(Field.from_descriptor(descriptor))
                self.resource.schema = schema

    def prepare_index(self):
        if self.with_metadata:
            sa = platform.sqlalchemy
            index = self.metadata.tables.get(INDEX_NAME)
            if index is None:
                index = sa.Table(
                    INDEX_NAME,
                    self.metadata,
                    sa.Column("path", sa.Text, primary_key=True),
                    sa.Column("table_name", sa.Text, unique=True),
                    sa.Column("updated", sa.DateTime),
                    sa.Column("resource", sa.Text),
                    sa.Column("report", sa.Text),
                )
                index.create(self.connection)
            return index

    def prepare_table(self, *, index: Optional[Table] = None):
        table_name = self.table_name

        # Sync table name with index (retrieve or ensure dedup)
        if index is not None:
            assert not table_name, '"table_name" is not supported with metadata'
            assert self.resource.path, '"resource.path" is required with metadata'
            found = False
            table_names = []
            template = f"{table_name}%s"
            table_name = self.resource.name
            query = index.select().with_only_columns([index.c.path, index.c.table_name])
            records = self.connection.execute(query)
            for record in records:
                table_names.append(record.table_name)
                if record.path == self.resource.path:
                    table_name = record.table_name
                    found = True
            if not found:
                suffix = 1
                while table_name in table_names:
                    table_name = template % suffix
                    suffix += 1

        # Remove existing table
        assert table_name, '"table_name" is requried'
        existing_table = self.metadata.tables.get(table_name)
        if existing_table is not None:
            existing_table.drop(self.connection)
            self.metadata.remove(existing_table)

        # Create new table
        table = self.mapper.write_schema(
            self.resource.schema,
            table_name=table_name,  # type: ignore
            with_row_number=index is not None,
        )
        table.to_metadata(self.metadata)
        table.create(self.connection)

        return table

    def index_resource(self, table: Table, *, index: Optional[Table] = None):
        raise NotImplementedError()


class GeneralIndexer(Indexer):

    # Index

    def index_resource(self, table: Table, *, index: Optional[Table] = None):
        buffer = []

        # Write row
        def callback(row):
            cells = self.mapper.write_row(row)
            if index is not None:
                cells.insert(0, row.row_number)
            buffer.append(cells)
            if len(buffer) > BUFFER_SIZE:
                self.connection.execute(table.insert().values(buffer))
                buffer.clear()
            self.report_progress(f"{self.resource.stats.rows} rows")

        # Validate/iterate
        report = self.resource.validate(callback=callback)
        if len(buffer):
            self.connection.execute(table.insert().values(buffer))

        # Register resource
        if index is not None:
            self.connection.execute(index.delete(index.c.table_name == table.name))
            self.connection.execute(
                index.insert().values(
                    path=self.resource.path,
                    table_name=table.name,
                    updated=datetime.now(),
                    resource=self.resource.to_json(),
                    report=report.to_json(),
                )
            )


class FastSqliteIndexer(Indexer):

    # Index

    def index_resource(self, table: Table, *, index: Optional[Table] = None):
        assert not index, "Metadata indexing is not supported in fast mode"
        # --csv and --skip options for .import are available from sqlite3@3.32
        # https://github.com/simonw/sqlite-utils/issues/297#issuecomment-880256058
        url = platform.sqlalchemy.engine.make_url(self.database_url)
        sql_command = f".import '|cat -' {table.name}"
        command = ["sqlite3", "-csv", url.database, sql_command]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        for line_number, line in enumerate(self.resource.byte_stream, start=1):
            if line_number > 1:
                process.stdin.write(line)  # type: ignore
            self.report_progress(f"{self.resource.stats.bytes} bytes")
        process.stdin.close()  # type: ignore
        process.wait()


class FastPostgresIndexer(Indexer):

    # Index

    def index_resource(self, table: Table, *, index: Optional[Table] = None):
        assert not index, "Metadata indexing is not supported in fast mode"
        with platform.psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                query = 'COPY "%s" FROM STDIN CSV HEADER' % table.name
                with cursor.copy(query) as copy:  # type: ignore
                    while True:
                        chunk = self.resource.read_bytes(size=BLOCK_SIZE)
                        if not chunk:
                            break
                        copy.write(chunk)
                        self.report_progress(f"{self.resource.stats.bytes} bytes")
