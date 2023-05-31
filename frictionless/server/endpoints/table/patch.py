from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router
from ..record import read as record_read
from . import export as table_export
from ... import models


class Props(BaseModel):
    path: str
    history: models.History


class Result(BaseModel):
    path: str


@router.post("/table/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    sa = platform.sqlalchemy

    # Write table
    record = record_read.action(project, record_read.Props(path=props.path)).record
    with db.engine.begin() as conn:
        table = db.metadata.tables[record.name]
        for change in props.history.changes:
            if change.type == "cell-update":
                conn.execute(
                    sa.update(table)
                    .where(table.c._rowNumber == change.rowNumber)
                    .values(**{change.fieldName: change.value})
                )

    # Export table
    path = table_export.action(project, table_export.Props(path=props.path)).path

    return Result(path=path)
