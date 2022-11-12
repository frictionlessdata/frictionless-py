from __future__ import annotations
import json
from typing import TYPE_CHECKING
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


# TODO: support timezones


def index(self: Resource, database_url: str, *, table_name: str):
    """Index resource into a database"""
    with self, platform.psycopg.connect(database_url) as connection:
        engine = platform.sqlalchemy.create_engine(database_url)
        mapper = platform.frictionless_formats.sql.SqlMapper()
        sql = platform.sqlalchemy_schema

        # Json dumper
        class JsonDumper(platform.psycopg.adapt.Dumper):
            def dump(self, data):
                return json.dumps(data).encode()

        # Register dumpers
        connection.adapters.register_dumper(dict, JsonDumper)

        # Write metadata
        table = mapper.from_schema(self.schema, engine=engine, table_name=table_name)
        with connection.cursor() as cursor:
            cursor.execute(str(sql.DropTable(table, bind=engine, if_exists=True)))
            cursor.execute(str(sql.CreateTable(table, bind=engine)))

        # Write data
        with connection.cursor() as cursor:
            with cursor.copy('COPY "%s" FROM STDIN' % table_name) as copy:
                for row in self.row_stream:
                    copy.write_row(row.to_list())
