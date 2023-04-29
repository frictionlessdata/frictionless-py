import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel):
    source: str
    target: Optional[str] = None
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/file/move")
def server_file_move(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Folder
    if props.folder:
        if not fs.get_fullpath(props.folder).exists():
            raise FrictionlessException("Folder doesn't exist")

    # Source
    source = fs.get_fullpath(props.source)
    if not source.exists():
        raise FrictionlessException("Source doesn't exist")

    # Target
    target = fs.get_fullpath(props.folder, props.target, deduplicate=props.deduplicate)
    if target.is_file() and target.exists():
        raise FrictionlessException("Target already exists")

    # Move
    shutil.move(source, target)
    path = fs.get_path(target)

    return Result(path=path)
