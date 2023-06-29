from __future__ import annotations

import os

from fastapi import Request
from pydantic import BaseModel

from ... import helpers
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    text: str


class Result(BaseModel, extra="forbid"):
    text: str


@router.post("/script/execute")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.path)
    with helpers.capture_stdout(cwd=os.path.dirname(fullpath)) as stdout:
        exec(props.text, {}, {})
    text = stdout.getvalue().strip()

    return Result(text=text)
