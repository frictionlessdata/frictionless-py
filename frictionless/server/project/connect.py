from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


# TODO: have one of connect/create?
# TODO: protect against many projects creation


class ProjectConnectProps(BaseModel):
    session: Optional[str]


@router.post("/project/connect")
def server_project_connect(request: Request, props: ProjectConnectProps):
    try:
        project = request.app.get_project(session=props.session)
    except Exception:
        project = request.app.get_project()
    return dict(session=project.session)
