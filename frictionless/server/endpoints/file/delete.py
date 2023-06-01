from __future__ import annotations
import os
import shutil
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

    # Delete record
    helpers.delete_record(project, path=props.path)

    # Delete file
    fullpath = fs.get_fullpath(props.path)
    if not fullpath.exists():
        raise FrictionlessException("file doesn't exist")
    delete = shutil.rmtree if fullpath.is_dir() else os.remove
    delete(fullpath)
    path = fs.get_path(fullpath)

    return Result(path=path)
