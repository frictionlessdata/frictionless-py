from __future__ import annotations
import json
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    report: Optional[IDescriptor]


@router.post("/report/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    sa = platform.sqlalchemy

    with db.engine.begin() as conn:
        query = sa.select(db.artifacts.c.report).where(db.artifacts.c.id == props.id)
        value = conn.execute(query).scalar_one_or_none()
        if not value:
            return Result(report=None)
        report = json.loads(value)

    return Result(report=report)
