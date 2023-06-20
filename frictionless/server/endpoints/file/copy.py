from __future__ import annotations

import shutil
from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ... import helpers
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    toPath: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/file/copy")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata

    # Get source
    source = fs.get_fullpath(props.path)
    if not source.is_file():
        raise FrictionlessException("Source doesn't exist")

    # Get target
    target = fs.get_fullpath(props.toPath) if props.toPath else fs.basepath
    if target.is_dir():
        target = target / source.name
    if props.deduplicate:
        target = fs.deduplicate_fullpath(target, suffix="copy")
    if target.exists():
        raise FrictionlessException("Target already exists")

    # Copy file
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, target)

    # Copy record
    toPath = fs.get_path(target)
    record = helpers.read_record(project, path=props.path)
    if record:
        record.name = helpers.name_record(project, path=toPath)
        record.path = toPath
        record.resource["path"] = toPath
        md.write_document(name=record.name, type="record", descriptor=record.dict())

    return Result(path=toPath)
