from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IView
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    view: IView


class Result(BaseModel):
    path: str


@router.post("/view/write")
def server_view_write(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.write_view(props.path, view=props.view)
    return Result(path=props.path)
