from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....resources import TableResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    source: str
    target: str


class Result(BaseModel):
    path: str


@router.post("/table/export")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: rework
# TODO: This is a placeholder code for export and we need to export it from database.
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    assert fs.is_filename(props.target)  # type: ignore
    source = fs.get_fullpath(props.source)
    target = fs.get_fullpath(props.target)
    TableResource(path=source).write(target)  # type: ignore

    return Result(path=target)  # type: ignore
