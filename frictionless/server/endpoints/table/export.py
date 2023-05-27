from __future__ import annotations
from typing import Optional
from fastapi import Request
from pydantic import BaseModel
from ....formats.sql import SqlControl
from ....resources import TableResource
from ...project import Project
from ...router import router
from ..record import read


class Props(BaseModel):
    path: str
    toPath: Optional[str] = None


class Result(BaseModel):
    path: str


@router.post("/table/export")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database

    record = read.action(project, read.Props(path=props.path)).record
    target = fs.get_fullpath(props.toPath or props.path)
    control = SqlControl(table=record.name, with_metadata=True)
    resource = TableResource(path=db.database_url, control=control)
    resource.write_table(path=str(target))

    path = fs.get_path(target)
    return Result(path=path)
