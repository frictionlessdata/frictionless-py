from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from .... import helpers


class Props(BaseModel):
    path: str
    folder: Optional[str] = None


class Result(BaseModel):
    path: str


@router.post("/folder/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_secure_fullpath(props.folder, props.path)
    if fs.is_existent(fullpath):
        raise FrictionlessException("Folder already exists")
    helpers.create_folder(fullpath)
    path = fs.get_secure_relpath(fullpath)

    return Result(path=path)
