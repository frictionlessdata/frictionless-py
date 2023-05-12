from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform
from ..interfaces import IQueryData
from .. import settings

if TYPE_CHECKING:
    from sqlalchemy import MetaData, Table
    from sqlalchemy.engine import Engine
    from ...formats.sql import SqlMapper
    from ..project import Project


class Database:
    database_url: str
    engine: Engine
    mapper: SqlMapper
    metadata: MetaData
    artifacts: Table

    def __init__(self, project: Project):
        sa = platform.sqlalchemy
        sql = platform.frictionless_formats.sql
        self.database_url = f"sqlite:///{project.private / 'database.db'}"
        self.engine = sa.create_engine(self.database_url)
        self.mapper = sql.SqlMapper(self.engine.dialect.name)
        with self.engine.begin() as conn:
            self.metadata = sa.MetaData()
            self.metadata.reflect(conn, views=True)

            # Ensure artifacts table
            artifacts = self.metadata.tables.get(settings.ARTIFACTS_IDENTIFIER)
            if artifacts is None:
                artifacts = sa.Table(
                    settings.ARTIFACTS_IDENTIFIER,
                    self.metadata,
                    sa.Column("id", sa.Text),
                    sa.Column("stats", sa.Text),
                    sa.Column("report", sa.Text),
                )
                self.metadata.create_all(conn, tables=[artifacts])
            self.artifacts = artifacts

    # General

    def query(self, query: str) -> IQueryData:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            result = conn.execute(sa.text(query))
            header = list(result.keys())
            rows = [row.asdict() for row in result]
            return IQueryData(header=header, rows=rows)
