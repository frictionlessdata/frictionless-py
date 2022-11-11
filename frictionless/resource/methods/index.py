from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


def index(self: Resource, database_url: str):
    """Index resource into a database"""
    with self:
        engine = platform.sqlalchemy.create_engine(database_url)
        cursor = engine.raw_connection().cursor()
        mapper = platform.frictionless_formats.sql.SqlMapper()

        # Write metadata
        assert self.name  # guaranteed by open
        table = mapper.from_schema(self.schema, engine=engine, table_name=self.name)
        table.metadata.create_all(engine)  # type: ignore

        # Write data
