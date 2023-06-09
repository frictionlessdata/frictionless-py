from __future__ import annotations
import os
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel):
    path: str


class Result(BaseModel):
    path: str


@router.post("/file/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Ensure file exists
    fullpath = fs.get_fullpath(props.path)
    if not fullpath.is_file():
        raise FrictionlessException("file doesn't exist")

    # Delete record
    helpers.delete_record(project, path=props.path)

    # Delete file
    os.remove(fullpath)

    path = fs.get_path(fullpath)
    return Result(path=path)
