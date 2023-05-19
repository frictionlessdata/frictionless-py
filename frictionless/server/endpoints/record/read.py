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
    record: Optional[models.Record]


@router.post("/record/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: merge here report/read and stats/read?
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    descriptor = md.read_document(id=props.id, type="record")
    if not descriptor:
        return Result(record=None)
    record = models.Record.parse_obj(descriptor)

    return Result(record=record)
