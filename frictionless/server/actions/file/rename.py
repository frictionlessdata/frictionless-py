from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    name: str


class Result(BaseModel):
    path: str


@router.post("/file/rename")
def server_file_rename(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.rename_file(props.path, name=props.name)
    return Result(path=path)
