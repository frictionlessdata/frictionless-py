from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel):
    path: str
    text: str


class Result(BaseModel):
    path: str


@router.post("/text/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Forbid overwriting
    if props.path and helpers.test_file(project, path=props.path):
        raise FrictionlessException("file already exists")

    # Write contents
    path = helpers.write_text(project, path=props.path, text=props.text)

    return Result(path=path)
