from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import models
from . import read


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    record = read.action(project, read.Props(id=props.id)).record
    if not record:
        raise FrictionlessException("record does not exist")
    md.delete_document(id=record.id, type="record")

    return Result(record=record)
