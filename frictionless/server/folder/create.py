from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    name: str
    folder: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/folder/create")
def server_file_create_folder(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = props.name
    if props.folder:
        path = str(Path(props.folder) / path)
    path = project.folder_create(path)
    return Result(path=path)
