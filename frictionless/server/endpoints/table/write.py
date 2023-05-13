from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    tablePatch: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/table/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: implement
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database

    print(fs)
    print(db)

    return Result(path=props.path)
