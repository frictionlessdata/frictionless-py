from __future__ import annotations
import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    source: str
    target: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/file/copy")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: copy resource as well?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Source
    source = fs.get_fullpath(props.source)
    if not source.exists():
        raise FrictionlessException("Source doesn't exist")

    # Target
    target = fs.get_fullpath(props.target) if props.target else fs.root
    if target.is_file():
        raise FrictionlessException("Target already exists")
    if target.is_dir():
        target = target / source.name
        if props.deduplicate:
            target = fs.deduplicate_fullpath(target, suffix="copy")

    # Copy
    copy = shutil.copytree if source.is_dir() else shutil.copy
    copy(source, target)

    path = fs.get_path(target)
    return Result(path=path)
