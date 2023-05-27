from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor
from ..record import read


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    report: IDescriptor


@router.post("/report/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database

    record = read.action(project, read.Props(path=props.path)).record
    report = db.read_artifact(name=record.name, type="report")
    if not report:
        raise FrictionlessException("report does no exist")

    return Result(report=report)
