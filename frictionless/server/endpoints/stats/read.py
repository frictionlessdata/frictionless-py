from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    stats: Optional[IDescriptor]


@router.post("/stats/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    stats = db.read_artifact(id=props.id, type="stats")
    return Result(stats=stats)
