from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFile
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    file: Optional[IFile]


@router.post("/file/index")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: implement after select
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database
    pass
