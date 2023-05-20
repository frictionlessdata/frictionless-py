from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import models
from . import read


class Props(BaseModel, extra="forbid"):
    name: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    record = read.action(project, read.Props(name=props.name)).record
    if not record:
        raise FrictionlessException("record does not exist")
    md.delete_document(name=record.name, type="record")

    return Result(record=record)
