from __future__ import annotations
import attrs
import subprocess
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Callable
from ...exception import FrictionlessException
from ...schema import Schema, Field
from ...project import Database
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource
    from sqlalchemy import Table


BLOCK_SIZE = 8096
BUFFER_SIZE = 1000


def index(
    self: Resource,
    database_url: str,
    *,
    table_name: Optional[str] = None,
    fast: bool = False,
    qsv: Optional[str] = None,
    with_metadata: bool = False,
    use_fallback: bool = False,
    on_progress: Optional[Callable[[str], None]] = None,
):
    """Index resource into a database"""

    # Prepare url
    if "://" not in database_url:
        database_url = f"sqlite:///{database_url}"
    url = platform.sqlalchemy.engine.make_url(database_url)

    # Metadata mode
    if with_metadata:
        assert not table_name, "Table name is not supported with metadata"
        database = Database(database_url)
        database.create_record(self, on_progress=on_progress)
        return

    # Select indexer
    if not fast:
        Indexer = GeneralIndexer
    elif url.drivername.startswith("sqlite"):
        Indexer = FastSqliteIndexer
    elif url.drivername.startswith("postgresql"):
        Indexer = FastPostgresIndexer
    else:
        raise FrictionlessException("Fast mode is only supported for Postgres/Sqlite")

    # Run indexer
    indexer = Indexer(
        resource=self,
        database_url=database_url,
        table_name=table_name,
        qsv=qsv,
        use_fallback=use_fallback,
        on_progress=on_progress,
    )
    indexer.index()


# Internal


@attrs.define(kw_only=True)
class Indexer:
    resource: Resource
    database_url: str
    table_name: Optional[str] = None
    qsv: Optional[str] = None
    use_fallback: bool = False
    on_progress: Optional[Callable[[str], None]] = None

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
        if self.on_progress:
            self.on_progress(message)

    # Index

    def index(self):
        self.prepare_resource()
        with self.resource:
            with self.connection.begin():
                table = self.prepare_table()
                try:
                    self.index_resource(table)
                except platform.sqlalchemy_exc.SQLAlchemyError:
                    if self.use_fallback:
                        self.fast = False
                        self.index_resource(table)

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

    def prepare_table(self):

        # Remove existing table
        existing_table = self.metadata.tables.get(self.table_name)
        if existing_table is not None:
            existing_table.drop(self.connection)
            self.metadata.remove(existing_table)

        # Create new table
        table = self.mapper.write_schema(
            self.resource.schema,
            table_name=self.table_name,  # type: ignore
            with_row_number=index is not None,
        )
        table.to_metadata(self.metadata)
        table.create(self.connection)

        return table

    def index_resource(self, table: Table):
        raise NotImplementedError()


class GeneralIndexer(Indexer):

    # Index

    def index_resource(self, table: Table):
        buffer = []
        for row in self.resource.row_stream:
            cells = self.mapper.write_row(row)
            if index is not None:
                cells.insert(0, row.row_number)
            buffer.append(cells)
            if len(buffer) > BUFFER_SIZE:
                self.connection.execute(table.insert().values(buffer))
                buffer.clear()
            self.report_progress(f"{self.resource.stats.rows} rows")
        if len(buffer):
            self.connection.execute(table.insert().values(buffer))


class FastSqliteIndexer(Indexer):

    # Index

    def index_resource(self, table: Table):
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

    def index_resource(self, table: Table):
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
