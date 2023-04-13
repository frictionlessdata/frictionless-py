from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    name: str
    folder: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/folder/create")
def server_folder_create(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.create_folder(props.name, folder=props.folder)
    return Result(path=path)
