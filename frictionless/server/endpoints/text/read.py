from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ... import helpers
from ...project import Project
from ...router import router

# TODO: use detected resource.encoding if indexed


class Props(BaseModel, extra="forbid"):
    path: str
    size: Optional[int]


class Result(BaseModel, extra="forbid"):
    text: str


@router.post("/text/read")
def server_text_read(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    text = helpers.read_text(project, path=props.path, size=props.size)
    return Result(text=text)
