from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ....resource import Resource
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel):
    id: str
    resource: IDescriptor


class Result(BaseModel):
    id: str


@router.post("/resource/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: validata id,datatype,etc
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    report = Resource.validate_descriptor(props.resource)
    if not report.valid:
        raise FrictionlessException("resource is not valid,")
    md.write_document(id=props.id, type="resource", descriptor=props.resource)

    return Result(id=props.id)
