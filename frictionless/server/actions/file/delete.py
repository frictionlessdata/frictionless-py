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


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database

    db.delete_record(props.path)
    fullpath = fs.get_secure_fullpath(props.path)
    # File
    if fs.is_file(fullpath):
        os.remove(fullpath)
    # Folder
    elif fs.is_folder(fullpath):
        shutil.rmtree(fullpath)
    # Missing
    else:
        FrictionlessException("file doesn't exist")
    path = fs.get_secure_relpath(fullpath)

    return Result(path=path)
