from __future__ import annotations
import attrs
import subprocess
from subprocess import PIPE
from typing import TYPE_CHECKING, Optional
from ...exception import FrictionlessException
from ...platform import platform
from ..qsv import QsvAdapter
from .interfaces import IOnProgress, IOnRow
from .adapter import SqlAdapter
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource
    from ...table import Row


@attrs.define(kw_only=True)
class SqlIndexer:
    resource: Resource
    database_url: str
    table_name: str
    fast: bool = False
    qsv_path: Optional[str] = None
    use_fallback: bool = False
    on_row: Optional[IOnRow] = None
    on_progress: Optional[IOnProgress] = None
    adapter: SqlAdapter = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.adapter = SqlAdapter(platform.sqlalchemy.create_engine(self.database_url))

    # Index

    def index(self):
        self.prepare_resource()
        with self.resource:
            self.create_table()
            while True:
                try:
                    self.populate_table()
                    break
                except Exception:
                    if self.fast and self.use_fallback:
                        self.fast = False
                        continue
                    self.delete_table()
                    raise

    def prepare_resource(self):
        if self.qsv_path:
            adapter = QsvAdapter(self.qsv_path)
            schema = adapter.read_schema(self.resource)
            self.resource.schema = schema

    def create_table(self):
        self.adapter.write_schema(
            self.resource.schema, table_name=self.table_name, force=True
        )

    def populate_table(self):
        if not self.fast:
            self.populate_table_base()
        else:
            self.populate_table_fast()

    def populate_table_base(self):
        self.adapter.write_row_stream(
            self.resource.row_stream, table_name=self.table_name, on_row=self.report_row
        )

    def populate_table_fast(self):
        url = platform.sqlalchemy.engine.make_url(self.database_url)
        if url.drivername.startswith("sqlite"):
            return self.populate_table_fast_sqlite()
        elif url.drivername.startswith("postgresql"):
            return self.populate_table_fast_postgresql()
        raise FrictionlessException("Fast mode is only supported for Postgres/Sqlite")

    def populate_table_fast_sqlite(self):
        sql_command = f".import '|cat -' \"{self.table_name}\""
        command = ["sqlite3", "-csv", self.adapter.engine.url.database, sql_command]
        process = subprocess.Popen(command, stdin=PIPE, stdout=PIPE)
        for line_number, line in enumerate(self.resource.byte_stream, start=1):
            if line_number > 1:
                process.stdin.write(line)  # type: ignore
            self.report_progress(f"{self.resource.stats.bytes} bytes")
        process.stdin.close()  # type: ignore
        process.wait()

    def populate_table_fast_postgresql(self):
        with platform.psycopg.connect(self.database_url) as connection:
            with connection.cursor() as cursor:
                query = 'COPY "%s" FROM STDIN CSV HEADER' % self.table_name
                with cursor.copy(query) as copy:  # type: ignore
                    while True:
                        chunk = self.resource.read_bytes(size=settings.BLOCK_SIZE)
                        if not chunk:
                            break
                        copy.write(chunk)
                        self.report_progress(f"{self.resource.stats.bytes} bytes")

    def delete_table(self):
        self.adapter.delete_resource(self.table_name)

    # Progress

    def report_row(self, row: Row):
        if self.on_row:
            self.on_row(row)
        self.report_progress(f"{row.row_number} rows")

    def report_progress(self, message: str):
        if self.on_progress:
            self.on_progress(message)
