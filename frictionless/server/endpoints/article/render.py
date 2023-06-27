from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ... import helpers
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
    text = helpers.render_article(props.text)
    return Result(text=text)
