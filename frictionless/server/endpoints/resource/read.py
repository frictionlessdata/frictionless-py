from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import Request
from ....resources import JsonResource
from ....resource import Resource
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    resource: Optional[Dict[str, Any]]


@router.post("/resource/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: implement actual logic
def action(project: Project, props: Props) -> Result:
    md = project.metadata

    metadata = JsonResource(path=str(md.fullpath)).read_data()
    resource = metadata.get(props.id)
    if not resource:
        return Result(resource=None)
    resource = Resource.from_descriptor(resource)

    return Result(resource=resource.to_descriptor())
