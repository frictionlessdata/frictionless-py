from __future__ import annotations
from typing import TYPE_CHECKING
from frictionless.exception import FrictionlessException
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


BLOCK_SIZE = 8096


def index(
    self: Resource,
    database_url: str,
    *,
    table_name: str,
    fast: bool = False,
):
    """Index resource into a database"""
    sa = platform.sqlalchemy
    url = sa.engine.make_url(database_url)

    # Postgresql
    if url.drivername.startswith("postgresql"):
        engine = sa.create_engine(database_url)
        with self, platform.psycopg.connect(database_url) as connection:
            engine = platform.sqlalchemy.create_engine(database_url)
            mapper = platform.frictionless_formats.sql.SqlMapper(engine)
            sql = platform.sqlalchemy_schema

            # Write metadata
            table = mapper.write_schema(self.schema, table_name=table_name)
            with connection.cursor() as cursor:
                cursor.execute(str(sql.DropTable(table, bind=engine, if_exists=True)))  # type: ignore
                cursor.execute(str(sql.CreateTable(table, bind=engine)))  # type: ignore

            # Write data (fast)
            # TODO: raise if header is not in the first row
            if fast:
                with connection.cursor() as cursor:
                    query = 'COPY "%s" FROM STDIN CSV HEADER' % table_name
                    with cursor.copy(query) as copy:  # type: ignore
                        while True:
                            chunk = self.read_bytes(size=BLOCK_SIZE)
                            if not chunk:
                                break
                            copy.write(chunk)

            # Write data (general)
            else:
                with connection.cursor() as cursor:
                    query = 'COPY "%s" FROM STDIN' % table_name
                    with cursor.copy(query) as copy:  # type: ignore

                        # Write row
                        def callback(row):
                            cells = mapper.write_row(row)
                            copy.write_row(cells)

                        # Validate/iterate
                        self.validate(callback=callback)

    # Not supported
    else:
        raise FrictionlessException(f"not supported database: {url.drivername}")
