from __future__ import annotations
from typing import Optional
from fastapi import Request
from pydantic import BaseModel
from ....exception import FrictionlessException
from ....resource import Resource
from ...project import Project
from ...router import router
from ... import models
from ... import types

# TODO: replace by helpers
from . import read


class Props(BaseModel):
    path: str
    type: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel):
    record: models.Record


@router.post("/record/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: validate type
# TODO: run validation again?
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    record = read.action(project, read.Props(path=props.path)).record
    if props.type:
        record.type = props.type
    if props.resource:
        report = Resource.validate_descriptor(props.resource)
        if not report.valid:
            raise FrictionlessException("resource is not valid")
        record.resource = props.resource

    md.write_document(name=record.name, type="record", descriptor=record.dict())
    return Result(record=record)
