from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from typing import Optional
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel):
    path: str
    text: str
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/text/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = helpers.write_text(
        project, path=props.path, text=props.text, deduplicate=props.deduplicate
    )
    return Result(path=path)
