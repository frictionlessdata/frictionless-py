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
    sa = platform.sqlalchemy
    db = project.database

    record = db.select_record(props.path)
    assert record
    assert "tableName" in record
    table = db.metadata.tables[record["tableName"]]
    query = sa.select(sa.func.count()).select_from(table)
    if props.valid is not None:
        query = query.where(table.c._rowValid == props.valid)
    with db.engine.begin() as conn:
        count = conn.execute(query).scalar_one()

    return Result(count=count)
