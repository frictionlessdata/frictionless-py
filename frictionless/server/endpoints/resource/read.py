from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....resource import Resource
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    resource: Optional[IDescriptor]


@router.post("/resource/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    descriptor = md.read_document(id=props.id, type="resource")
    if not descriptor:
        return Result(resource=None)

    resource = Resource.from_descriptor(descriptor)
    return Result(resource=resource.to_descriptor())
