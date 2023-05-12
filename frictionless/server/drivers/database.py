from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform
from ..interfaces import IQueryData

if TYPE_CHECKING:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from ...formats.sql import SqlMapper
    from ..project import Project


class Database:
    database_url: str
    engine: Engine
    mapper: SqlMapper
    metadata: MetaData

    def __init__(self, project: Project):
        sa = platform.sqlalchemy
        fullpath = project.private / "database.db"
        sql = platform.frictionless_formats.sql
        self.database_url = f"sqlite:///{fullpath}"
        self.engine = sa.create_engine(self.database_url)
        self.mapper = sql.SqlMapper(self.engine.dialect.name)

    # General

    def query(self, query: str) -> IQueryData:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            result = conn.execute(sa.text(query))
            header = list(result.keys())
            rows = [row.asdict() for row in result]
            return IQueryData(header=header, rows=rows)
