from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....resources import ArticleResource
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    text: str
    rich: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    text: str


@router.post("/article/render")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    resource = ArticleResource(data=props.text)
    text = resource.render_article(rich=props.rich)
    return Result(text=text)
