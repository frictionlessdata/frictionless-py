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
    md = project.metadata
    db = project.database

    # Get source
    source = fs.get_fullpath(props.path)
    if not source.exists():
        raise FrictionlessException("Source doesn't exist")

    # Delete table/artifacts/record
    record = helpers.find_record(project, path=props.path)
    if record:
        db.delete_table(name=record.name)
        db.delete_artifact(name=record.name)
        md.delete_document(name=record.name, type="record")

    # Delete file
    delete = shutil.rmtree if source.is_dir() else os.remove
    delete(source)

    path = fs.get_path(source)
    return Result(path=path)
