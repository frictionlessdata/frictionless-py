from __future__ import annotations

import json
from typing import TYPE_CHECKING, Iterator, Optional, Tuple

from ... import helpers, types
from ...platform import platform
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
                    sa.Column("name", sa.Text, primary_key=True),
                    sa.Column("type", sa.Text, primary_key=True),
                    sa.Column("descriptor", sa.Text),
                )
                self.metadata.create_all(conn, tables=[artifacts])
            self.artifacts = artifacts

    # Artifacts

    def iter_artifacts(self, *, type: str) -> Iterator[Tuple[str, types.IDescriptor]]:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            query = sa.select(self.artifacts.c.name, self.artifacts.c.descriptor).where(
                self.artifacts.c.type == type,
            )
            for item in conn.execute(query).all():
                yield item.name, json.loads(item.descriptor)

    def delete_artifact(self, *, name: str, type: str):
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            query = sa.delete(self.artifacts).where(
                self.artifacts.c.name == name,
                self.artifacts.c.type == type,
            )
            conn.execute(query)

    def read_artifact(self, *, name: str, type: str) -> Optional[types.IDescriptor]:
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            text = conn.execute(
                sa.select(self.artifacts.c.descriptor).where(
                    self.artifacts.c.name == name,
                    self.artifacts.c.type == type,
                )
            ).scalar_one_or_none()
            if not text:
                return None
            descriptor = json.loads(text)
        return descriptor

    def write_artifact(self, *, name: str, type: str, descriptor: types.IDescriptor):
        sa = platform.sqlalchemy
        with self.engine.begin() as conn:
            self.delete_artifact(name=name, type=type)
            conn.execute(
                sa.insert(self.artifacts).values(
                    name=name, type=type, descriptor=helpers.to_json(descriptor)
                )
            )

    # Tables

    def delete_table(self, *, name: str):
        table = self.get_table(name=name)
        if table is not None:
            with self.engine.begin() as conn:
                table.drop(conn)

    def get_table(self, *, name: str):
        return self.metadata.tables.get(name, None)
