from __future__ import annotations
from typing import Optional
from fastapi import Request
from pydantic import BaseModel
from ....exception import FrictionlessException
from ....resource import Resource
from ...project import Project
from ...router import router
from ... import helpers
from ... import models
from ... import types


class Props(BaseModel):
    path: str
    type: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel):
    record: models.Record


@router.post("/file/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: validate type
# TODO: run validation again?
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    # Read record
    record = helpers.read_record_or_raise(project, path=props.path)

    # Write record
    if props.type:
        record.type = props.type
    if props.resource:
        report = Resource.validate_descriptor(props.resource)
        if not report.valid:
            raise FrictionlessException("resource is not valid")
        record.resource = props.resource
    md.write_document(name=record.name, type="record", descriptor=record.dict())

    return Result(record=record)
