from __future__ import annotations
from fastapi import Request
from ..project import Project
from ..router import router


# TODO: protect against many projects creation


@router.post("/project/create")
def server_project(request: Request):
    config = request.app.config
    project = Project(config)
    return dict(session=project.session)
