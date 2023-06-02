from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from typing import Optional
from ....resources import ArticleResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    text: str
    rich: Optional[bool] = None


class Result(BaseModel):
    text: str


@router.post("/article/render")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    resource = ArticleResource(data=props.text)
    text = resource.render_article(rich=props.rich)
    return Result(text=text)
