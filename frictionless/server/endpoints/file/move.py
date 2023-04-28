import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/file/move")
def server_file_move(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Source
    source = fs.get_fullpath(props.path)
    if not fs.is_existent(source):
        raise FrictionlessException("Source doesn't exist")

    # Target
    target = fs.get_fullpath(props.folder, props.path, deduplicate=props.deduplicate)
    if fs.is_existent(target):
        raise FrictionlessException("Target already exists")

    # Move
    shutil.move(source, target)
    path = fs.get_relpath(target)

    return Result(path=path)
