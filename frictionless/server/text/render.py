from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    text: str


@router.post("/text/render")
def server_text_render(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    text = project.render_text(props.path)
    return Result(text=text)
