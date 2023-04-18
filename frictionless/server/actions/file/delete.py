from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    path: str


@router.post("/file/delete")
def server_file_delete(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    project.delete_file(props.path)
    return Result(path=props.path)
