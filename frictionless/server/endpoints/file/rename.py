from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from .... import helpers


class Props(BaseModel):
    path: str
    name: str


class Result(BaseModel):
    path: str


@router.post("/file/rename")
def server_file_rename(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    folder = fs.get_folder(props.path)
    if folder:
        folder = fs.get_fullpath(folder)
        assert fs.is_folder(folder)
    source = fs.get_fullpath(props.path)
    target = fs.get_fullpath(folder, props.name, deduplicate="renamed")

    # File
    if fs.is_file(source):
        helpers.move_file(source, target)
    # Folder
    elif fs.is_folder(source):
        helpers.move_folder(source, target)
    # Missing
    else:
        raise FrictionlessException("file doesn't exist")
    path = fs.get_relpath(target)

    return Result(path=path)
