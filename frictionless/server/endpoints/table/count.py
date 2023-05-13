from __future__ import annotations
from tinydb import Query
from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    valid: Optional[bool]


class Result(BaseModel):
    count: int


@router.post("/table/count")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata
    db = project.database
    sa = platform.sqlalchemy

    descriptor = md.find_document(type="resource", query=Query().path == props.path)
    assert descriptor
    id = descriptor["id"]
    table = db.metadata.tables[id]
    query = sa.select(sa.func.count()).select_from(table)
    if props.valid is not None:
        query = query.where(table.c._rowValid == props.valid)
    with db.engine.begin() as conn:
        count = conn.execute(query).scalar_one()

    return Result(count=count)
