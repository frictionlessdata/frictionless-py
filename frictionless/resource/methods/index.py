from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


def index(self: Resource, database_url: str):
    """Index resource into a database"""
    with self, platform.psycopg.connect(database_url) as connection:
        engine = platform.sqlalchemy.create_engine(database_url)
        mapper = platform.frictionless_formats.sql.SqlMapper()
        sql = platform.sqlalchemy_schema

        # Write metadata
        assert self.name  # guaranteed for open resource
        table = mapper.from_schema(self.schema, engine=engine, table_name=self.name)
        with connection.cursor() as cursor:
            cursor.execute(str(sql.DropTable(table, if_exists=True)))
            cursor.execute(str(sql.CreateTable(table)))

        # Write data
        with connection.cursor() as cursor:
            with cursor.copy("COPY %s FROM STDIN" % self.name) as copy:
                for row in self.row_stream:
                    copy.write_row(row.to_list())
