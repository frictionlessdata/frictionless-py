from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/folder/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Folder
    if props.folder:
        if not fs.get_fullpath(props.folder).exists():
            raise FrictionlessException("Folder doesn't exist")

    # Target
    target = fs.get_fullpath(props.folder, props.path, deduplicate=props.deduplicate)
    if target.exists():
        raise FrictionlessException("Folder already exists")

    # Create
    target.mkdir(parents=True)
    path = fs.get_path(target)

    return Result(path=path)
