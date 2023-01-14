from __future__ import annotations
import attrs
import subprocess
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Type, Callable
from ...exception import FrictionlessException
from ...schema import Schema, Field
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


BLOCK_SIZE = 8096
INDEX_NAME = "index"


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
    ActualIndexer: Optional[Type[Indexer]] = None
    if url.drivername.startswith("postgresql"):
        ActualIndexer = FastPostgresIndexer if fast else PostgresIndexer
    if url.drivername.startswith("sqlite"):
        ActualIndexer = FastSqliteIndexer if fast else SqliteIndexer
    if not ActualIndexer:
        raise FrictionlessException(f"not supported database: {url.drivername}")

    # Run indexer
    indexer = ActualIndexer(
        resource=self,
        database_url=database_url,
        table_name=table_name,
        qsv=qsv,
        callback=callback,
        with_metadata=with_metadata,
    )
    indexer.index_resource()


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
    def engine(self):
        return platform.sqlalchemy.create_engine(self.database_url)

    @cached_property
    def metadata(self):
        metadata = platform.sqlalchemy.MetaData(self.engine)
        metadata.reflect()
        return metadata

    @cached_property
    def mapper(self):
        return platform.frictionless_formats.sql.SqlMapper(self.engine)

    @cached_property
    def index(self):
        sa = platform.sqlalchemy
        index = self.metadata.tables.get(INDEX_NAME)
        if index is None:
            index = sa.Table(INDEX_NAME, self.metadata, sa.Column("path", sa.Text))
            index.create()
        return index

    @cached_property
    def table(self):
        table_name = self.table_name or self.resource.name
        assert table_name
        existing_table = self.metadata.tables.get(table_name)
        if existing_table is not None:
            existing_table.drop()
        table = self.mapper.write_schema(
            self.resource.schema,
            table_name=table_name,
            metadata=self.metadata,
        )
        table.create()
        return table

    # Progress

    def report_progress(self, message: str):
        if self.callback:
            self.callback(message)

    # Index

    def index_resource(self):
        self.prepare_resource()
        # TODO: draft
        if self.with_metadata:
            self.index
        with self.resource:
            self.transfer_resource()

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

    def transfer_resource(self):
        raise NotImplementedError()


class PostgresIndexer(Indexer):

    # Methods

    def transfer_resource(self):
        with platform.psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                query = 'COPY "%s" FROM STDIN' % self.table.name
                with cursor.copy(query) as copy:  # type: ignore

                    # Write row
                    def callback(row):
                        cells = self.mapper.write_row(row)
                        copy.write_row(cells)
                        self.report_progress(f"{self.resource.stats.rows} rows")

                    # Validate/iterate
                    self.resource.validate(callback=callback)


class FastPostgresIndexer(Indexer):

    # Methods

    def transfer_resource(self):
        with platform.psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                query = 'COPY "%s" FROM STDIN CSV HEADER' % self.table.name
                with cursor.copy(query) as copy:  # type: ignore
                    while True:
                        chunk = self.resource.read_bytes(size=BLOCK_SIZE)
                        if not chunk:
                            break
                        copy.write(chunk)
                        self.report_progress(f"{self.resource.stats.bytes} bytes")


class SqliteIndexer(Indexer):

    # Methods

    def transfer_resource(self):
        buffer = []
        buffer_size = 1000

        # Write row
        def callback(row):
            cells = self.mapper.write_row(row)
            buffer.append(cells)
            if len(buffer) > buffer_size:
                self.engine.execute(self.table.insert().values(buffer))
                buffer.clear()
            self.report_progress(f"{self.resource.stats.rows} rows")

        # Validate/iterate
        self.resource.validate(callback=callback)
        if len(buffer):
            self.engine.execute(self.table.insert().values(buffer))


class FastSqliteIndexer(Indexer):

    # Methods

    def transfer_resource(self):
        # --csv and --skip options for .import are available from sqlite3@3.32
        # https://github.com/simonw/sqlite-utils/issues/297#issuecomment-880256058
        url = platform.sqlalchemy.engine.make_url(self.database_url)
        sql_command = f".import '|cat -' {self.table.name}"
        command = ["sqlite3", "-csv", url.database, sql_command]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        for line_number, line in enumerate(self.resource.byte_stream, start=1):
            if line_number > 1:
                process.stdin.write(line)  # type: ignore
            self.report_progress(f"{self.resource.stats.bytes} bytes")
        process.stdin.close()  # type: ignore
        process.wait()
