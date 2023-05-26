from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router
from ..record import read
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
    fs = project.filesystem
    db = project.database
    sa = platform.sqlalchemy
    print(fs)
    print(db)

    record = read.action(project, read.Props(path=props.path)).record
    table = db.metadata.tables[record.name]

    with db.engine.begin() as conn:
        for change in props.history.changes:
            if change.type == "cell-update":
                conn.execute(
                    sa.update(table)
                    .where(table.c._rowNumber == change.rowNumber)
                    .values(**{change.fieldName: change.value})
                )

    return Result(path=props.path)
