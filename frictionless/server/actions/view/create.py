from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/view/create")
def server_view_render(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.create_view(path=props.path)
    return Result(path=path)
