from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ....resource import Resource
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    resource: IDescriptor


@router.post("/resource/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    metadata = md.read()
    descriptor = metadata.pop(props.id, None)
    if not descriptor:
        raise FrictionlessException("Resource doesn't exist")
    md.write(metadata)

    resource = Resource.from_descriptor(descriptor)
    return Result(resource=resource.to_descriptor())
