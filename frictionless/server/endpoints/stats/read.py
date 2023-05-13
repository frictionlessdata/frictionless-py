from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    stats: Optional[models.Stats]


@router.post("/stats/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    data = db.read_artifact(id=props.id, type="stats")
    if not data:
        return Result(stats=None)
    stats = models.Stats(**data)
    return Result(stats=stats)
