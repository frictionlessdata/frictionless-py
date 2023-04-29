import os
import shutil
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    path: str


@router.post("/file/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: shall we move db delection to resource.delete?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database

    # Database
    db.delete_record(props.path)

    # Source
    source = fs.get_fullpath(props.path)
    if not source.exists():
        raise FrictionlessException("Source doesn't exist")

    # Delete
    delete = shutil.rmtree if source.is_dir() else os.remove
    delete(source)

    path = fs.get_path(source)
    return Result(path=path)
