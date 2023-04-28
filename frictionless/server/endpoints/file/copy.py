from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from .... import helpers


class Props(BaseModel):
    path: str
    folder: Optional[str]
    newPath: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/file/copy")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: copy resource as well?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    name = fs.get_filename(props.path)
    folder = props.folder
    if folder:
        folder = fs.get_fullpath(folder)
        assert fs.is_folder(folder)
    source = fs.get_fullpath(props.path)
    target = fs.get_fullpath(folder, props.newPath or name, deduplicate="copy")

    # File
    if fs.is_file(source):
        helpers.copy_file(source, target)
    # Folder
    elif fs.is_folder(source):
        helpers.copy_folder(source, target)
    # Missing
    else:
        raise FrictionlessException("file doesn't exist")

    path = fs.get_relpath(target)
    return Result(path=path)
