from __future__ import annotations
import attrs
import subprocess
from subprocess import PIPE
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Callable
from ...exception import FrictionlessException
from ...platform import platform
from ..qsv import QsvAdapter

if TYPE_CHECKING:
    from ...resource import Resource
    from sqlalchemy import Table


BLOCK_SIZE = 8096
BUFFER_SIZE = 1000


# Currently, a base class is the only way to mix attrs and changed_property
@attrs.define(kw_only=True)
class SqlIndexerState:
    resource: Resource
    database_url: str
    table_name: str
    fast: bool = False
    qsv_path: Optional[str] = None
    use_fallback: bool = False
    on_progress: Optional[Callable[[str], None]] = None


class SqlIndexer(SqlIndexerState):
    @cached_property
    def mapper(self):
        # TODO: pass database_url
        return platform.frictionless_formats.sql.SqlMapper(self.engine)

    @cached_property
    def engine(self):
        return platform.sqlalchemy.create_engine(self.database_url)

    # TODO: use context manager to open/close connection
    @cached_property
    def connection(self):
        return self.engine.connect()

    @cached_property
    def metadata(self):
        metadata = platform.sqlalchemy.MetaData()
        metadata.reflect(self.connection)
        return metadata

    # Index

    def index(self):
        self.prepare_resource()
        with self.resource:
            table = self.prepare_table()
            while True:
                try:
                    self.populate_table(table)
                    break
                except Exception:
                    if self.fast and self.use_fallback:
                        self.fast = False
                        continue
                    self.rollback_table(table)
                    raise

    def prepare_resource(self):
        if self.qsv_path:
            adapter = QsvAdapter(self.qsv_path)
            schema = adapter.read_schema(self.resource)
            self.resource.schema = schema

    def prepare_table(self):
        existing_table = self.metadata.tables.get(self.table_name)
        if existing_table is not None:
            existing_table.drop(self.connection)
            self.metadata.remove(existing_table)
        table = self.mapper.write_schema(self.resource.schema, table_name=self.table_name)
        table.to_metadata(self.metadata)
        table.create(self.connection)
        return table

    def populate_table(self, table: Table):
        if not self.fast:
            self.populate_table_base(table)
        else:
            self.populate_table_fast(table)

    def populate_table_base(self, table: Table):
        buffer = []
        for row in self.resource.row_stream:
            cells = self.mapper.write_row(row)
            buffer.append(cells)
            if len(buffer) > BUFFER_SIZE:
                self.connection.execute(table.insert().values(buffer))
                buffer.clear()
            self.report_progress(f"{self.resource.stats.rows} rows")
        if len(buffer):
            self.connection.execute(table.insert().values(buffer))

    def populate_table_fast(self, table: Table):
        url = platform.sqlalchemy.engine.make_url(self.database_url)
        if url.drivername.startswith("sqlite"):
            return self.populate_table_fast_sqlite(table)
        elif url.drivername.startswith("postgresql"):
            return self.populate_table_fast_postgresql(table)
        raise FrictionlessException("Fast mode is only supported for Postgres/Sqlite")

    def populate_table_fast_sqlite(self, table: Table):
        sql_command = f".import '|cat -' \"{table.name}\""
        command = ["sqlite3", "-csv", self.engine.url.database, sql_command]
        process = subprocess.Popen(command, stdin=PIPE, stdout=PIPE)
        for line_number, line in enumerate(self.resource.byte_stream, start=1):
            if line_number > 1:
                process.stdin.write(line)  # type: ignore
            self.report_progress(f"{self.resource.stats.bytes} bytes")
        process.stdin.close()  # type: ignore
        process.wait()

    def populate_table_fast_postgresql(self, table: Table):
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

    def rollback_table(self, table: Table):
        table.drop(self.connection)
        self.metadata.remove(table)

    # Progress

    def report_progress(self, message: str):
        if self.on_progress:
            self.on_progress(message)
