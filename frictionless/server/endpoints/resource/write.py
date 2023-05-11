from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
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


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    metadata = md.read()
    resource = Resource.from_descriptor(props.resource)
    metadata[props.id] = resource.to_descriptor()
    md.write(metadata)

    return Result(id=props.id)
