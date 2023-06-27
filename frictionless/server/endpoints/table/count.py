from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....platform import platform
from ... import helpers
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    valid: Optional[bool]


class Result(BaseModel, extra="forbid"):
    count: int


@router.post("/table/count")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    sa = platform.sqlalchemy

    record = helpers.read_record_or_raise(project, path=props.path)
    table = db.metadata.tables[record.name]
    query = sa.select(sa.func.count()).select_from(table)
    if props.valid is not None:
        query = query.where(table.c._rowValid == props.valid)
    with db.engine.begin() as conn:
        count = conn.execute(query).scalar_one()

    return Result(count=count)
