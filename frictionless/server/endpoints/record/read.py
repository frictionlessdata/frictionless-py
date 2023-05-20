from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from tinydb import Query
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: merge here report/read and stats/read?
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    descriptor = md.find_document(type="record", query=Query().path == props.path)
    if not descriptor:
        raise FrictionlessException("record does no exist")
    record = models.Record.parse_obj(descriptor)

    return Result(record=record)
