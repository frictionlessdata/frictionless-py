from __future__ import annotations
import attrs
import subprocess
from subprocess import PIPE
from typing import TYPE_CHECKING, Optional, Callable
from ...exception import FrictionlessException
from ...platform import platform
from ..qsv import QsvAdapter
from . import settings

if TYPE_CHECKING:
    from sqlalchemy import MetaData, Table
    from sqlalchemy.engine import Engine
    from ...resource import Resource
    from .mapper import SqlMapper


@attrs.define(kw_only=True)
class SqlIndexer:
    resource: Resource
    database_url: str
    table_name: str
    fast: bool = False
    qsv_path: Optional[str] = None
    use_fallback: bool = False
    on_progress: Optional[Callable[[str], None]] = None
    engine: Engine = attrs.field(init=False)
    mapper: SqlMapper = attrs.field(init=False)
    metadata: MetaData = attrs.field(init=False)

    def __attrs_post_init__(self):
        sa = platform.sqlalchemy
        sql = platform.frictionless_formats.sql
        self.engine = sa.create_engine(self.database_url)
        self.mapper = sql.SqlMapper(self.engine.dialect.name)
        with self.engine.begin() as conn:
            self.metadata = sa.MetaData()
            self.metadata.reflect(conn, views=True)

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
        with self.engine.begin() as conn:
            existing_table = self.metadata.tables.get(self.table_name)
            if existing_table is not None:
                self.metadata.drop_all(conn, tables=[existing_table])
            table = self.mapper.write_schema(
                self.resource.schema, table_name=self.table_name
            )
            table.to_metadata(self.metadata)
            self.metadata.create_all(conn, tables=[table])
            return table

    def populate_table(self, table: Table):
        if not self.fast:
            self.populate_table_base(table)
        else:
            self.populate_table_fast(table)

    # TODO: reuse insert code from SqlAdapter?
    def populate_table_base(self, table: Table):
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            buffer = []
            for row in self.resource.row_stream:
                cells = self.mapper.write_row(row)
                buffer.append(cells)
                if len(buffer) > settings.BUFFER_SIZE:
                    conn.execute(sa.insert(table).values(buffer))
                    buffer.clear()
                self.report_progress(f"{self.resource.stats.rows} rows")
            if len(buffer):
                conn.execute(sa.insert(table).values(buffer))

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
                        chunk = self.resource.read_bytes(size=settings.BLOCK_SIZE)
                        if not chunk:
                            break
                        copy.write(chunk)
                        self.report_progress(f"{self.resource.stats.bytes} bytes")

    def rollback_table(self, table: Table):
        with self.engine.begin() as conn:
            self.metadata.drop_all(conn, tables=[table])

    # Progress

    def report_progress(self, message: str):
        if self.on_progress:
            self.on_progress(message)
