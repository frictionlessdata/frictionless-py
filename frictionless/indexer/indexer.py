from __future__ import annotations

import subprocess
from subprocess import PIPE
from typing import TYPE_CHECKING, Optional, Union

import attrs

from ..exception import FrictionlessException
from ..platform import platform
from . import settings, types

if TYPE_CHECKING:
    from sqlalchemy import Engine

    from ..formats.sql import SqlAdapter
    from ..report import Report
    from ..resources import TableResource
    from ..table import Row


@attrs.define(kw_only=True, repr=False)
class Indexer:
    resource: TableResource
    database: Union[str, Engine]
    table_name: str
    fast: bool = False
    qsv_path: Optional[str] = None
    use_fallback: bool = False
    with_metadata: bool = False
    on_row: Optional[types.IOnRow] = None
    on_progress: Optional[types.IOnProgress] = None
    adapter: SqlAdapter = attrs.field(init=False)

    def __attrs_post_init__(self):
        sa = platform.sqlalchemy
        if self.resource.format != "csv":
            self.fast = False
        engine = self.database
        if isinstance(engine, str):
            engine = sa.create_engine(engine)
        self.adapter = platform.frictionless_formats.SqlAdapter(engine)

    # Index

    def index(self) -> Optional[Report]:
        self.prepare_resource()
        with self.resource:
            # Index is resouce-based operation not supporting FKs
            if self.resource.schema.foreign_keys:
                self.resource.schema.foreign_keys = []
            self.create_table()
            while True:
                try:
                    return self.populate_table()
                except Exception:
                    if self.fast and self.use_fallback:
                        self.fast = False
                        continue
                    self.delete_table()
                    raise

    def prepare_resource(self):
        if self.qsv_path:
            adapter = platform.frictionless_formats.QsvAdapter(self.qsv_path)
            schema = adapter.read_schema(self.resource)
            self.resource.schema = schema

    def create_table(self):
        self.adapter.write_schema(
            self.resource.schema,
            table_name=self.table_name,
            force=True,
            with_metadata=self.with_metadata,
        )

    def populate_table(self) -> Optional[Report]:
        if self.fast:
            return self.populate_table_fast()
        if self.with_metadata:
            return self.populate_table_meta()
        return self.populate_table_base()

    def populate_table_base(self) -> None:
        self.adapter.write_row_stream(
            self.resource.row_stream,
            table_name=self.table_name,
            on_row=self.report_row,
        )

    def populate_table_meta(self) -> Report:
        return self.adapter.write_resource_with_metadata(
            self.resource,
            table_name=self.table_name,
            on_row=self.report_row,
        )

    def populate_table_fast(self) -> None:
        url = self.adapter.engine.url
        if url.drivername.startswith("sqlite"):
            return self.populate_table_fast_sqlite()
        elif url.drivername.startswith("postgresql"):
            return self.populate_table_fast_postgresql()
        raise FrictionlessException("Fast mode is only supported for Postgres/Sqlite")

    def populate_table_fast_sqlite(self):
        assert self.adapter.engine.url.database
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
        database_url = self.adapter.engine.url.render_as_string(hide_password=False)
        with platform.psycopg.connect(database_url) as connection:
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
            self.on_row(self.table_name, row)
        self.report_progress(f"{row.row_number} rows")

    def report_progress(self, message: str):
        if self.on_progress:
            self.on_progress(self.table_name, message)
