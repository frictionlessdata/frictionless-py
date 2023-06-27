from __future__ import annotations

import shutil

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/folder/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    from ... import endpoints

    # Check folder exists
    fullpath = fs.get_fullpath(props.path)
    if not fullpath.is_dir():
        raise FrictionlessException("folder not found")

    # List files inside
    result = endpoints.file.list.action(
        project,
        endpoints.file.list.Props(folder=props.path),
    )

    # Delete files inside
    for file in result.files:
        if file.type != "folder":
            endpoints.file.delete.action(
                project,
                endpoints.file.delete.Props(path=file.path),
            )

    # Delete folder
    shutil.rmtree(fullpath)

    path = fs.get_path(fullpath)
    return Result(path=path)
