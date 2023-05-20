from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel, extra="forbid"):
    name: str


class Result(BaseModel, extra="forbid"):
    report: Optional[IDescriptor]


@router.post("/report/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    report = db.read_artifact(name=props.name, type="report")
    return Result(report=report)
