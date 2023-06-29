from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....platform import platform
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    text: str
    rich: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    text: str


@router.post("/article/render")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    #  fs = project.filesystem

    #  fullpath = fs.get_fullpath(props.path)
    markdown = platform.marko.Markdown()
    markdown.use(platform.marko_ext_gfm.GFM)
    text = markdown.convert(props.text)

    return Result(text=text)
