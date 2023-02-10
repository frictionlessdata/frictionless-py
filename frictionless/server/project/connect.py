from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router

# TODO: protect against many projects creation


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    session: Optional[str]


@router.post("/project/connect", response_model_exclude_none=True)
def server_project_connect(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(session=props.session)
    return Result(session=project.session)
