from __future__ import annotations
import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ....helpers import ensure_dir
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel, extra="forbid"):
    path: str
    toPath: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/file/move")
def server_file_move(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata

    # Get source
    source = fs.get_fullpath(props.path)
    if not source.exists():
        raise FrictionlessException("Source doesn't exist")

    # Get target
    target = fs.get_fullpath(props.toPath) if props.toPath else fs.basepath
    if target.is_dir():
        target = target / source.name
    if props.deduplicate:
        target = fs.deduplicate_fullpath(target, suffix="copy")
    if target.exists():
        raise FrictionlessException("Target already exists")

    # Move file
    ensure_dir(str(target))
    shutil.move(source, target)
    path = fs.get_path(target)

    # Move record
    record = helpers.read_record(project, path=props.path)
    if record:
        record.path = path
        record.resource["path"] = path
        md.write_document(name=record.name, type="record", descriptor=record.dict())

    return Result(path=path)
