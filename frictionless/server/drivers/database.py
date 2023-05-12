from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
from ...platform import platform
from ..interfaces import IQueryData, IDescriptor
from ... import helpers
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
                    sa.Column("id", sa.Text, primary_key=True),
                    sa.Column("type", sa.Text, primary_key=True),
                    sa.Column("descriptor", sa.Text),
                )
                self.metadata.create_all(conn, tables=[artifacts])
            self.artifacts = artifacts

    def query(self, query: str) -> IQueryData:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            result = conn.execute(sa.text(query))
            header = list(result.keys())
            rows = [row.asdict() for row in result]
            return IQueryData(header=header, rows=rows)

    # Artifacts

    def delete_artifact(self, *, id: str, type: Optional[str] = None):
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            query = sa.delete(self.artifacts).where(self.artifacts.c.id == id)
            if type:
                query = query.where(self.artifacts.c.type == type)
            conn.execute(query)

    def read_artifact(self, *, id: str, type: str) -> Optional[IDescriptor]:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            text = conn.execute(
                sa.select(self.artifacts.c.descriptor).where(
                    self.artifacts.c.id == id,
                    self.artifacts.c.type == type,
                )
            ).scalar_one_or_none()
            if not text:
                return None
            descriptor = json.loads(text)
        return descriptor

    def write_artifact(self, *, id: str, type: str, descriptor: IDescriptor):
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            self.delete_artifact(id=id, type=type)
            conn.execute(
                sa.insert(self.artifacts).values(
                    id=id, type=type, descriptor=helpers.to_json(descriptor)
                )
            )
