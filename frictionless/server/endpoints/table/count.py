from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router
from ..record import read


class Props(BaseModel):
    path: str
    valid: Optional[bool]


class Result(BaseModel):
    count: int


@router.post("/table/count")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    sa = platform.sqlalchemy

    record = read.action(project, read.Props(path=props.path)).record
    table = db.metadata.tables[record.name]
    query = sa.select(sa.func.count()).select_from(table)
    if props.valid is not None:
        query = query.where(table.c._rowValid == props.valid)
    with db.engine.begin() as conn:
        count = conn.execute(query).scalar_one()

    return Result(count=count)
