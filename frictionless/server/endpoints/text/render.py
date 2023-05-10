from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from typing import Optional
from ....resources import TextResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    text: str
    livemark: Optional[bool] = None


class Result(BaseModel):
    text: str


@router.post("/text/render")
def server_text_render(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Render
    resource = TextResource(data=props.text)
    text = resource.render_text(livemark=props.livemark)

    return Result(text=text)
