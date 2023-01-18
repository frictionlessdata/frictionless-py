from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


# TODO: have one of connect/create?
# TODO: protect against many projects creation


class ProjectConnectProps(BaseModel):
    session: Optional[str]


@router.post("/project/connect")
def server_project_connect(request: Request, props: ProjectConnectProps):
    config = request.app.config
    try:
        project = Project(config, session=props.session)
    except Exception:
        project = Project(config)
    return dict(session=project.session)
