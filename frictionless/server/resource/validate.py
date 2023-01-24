from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..router import router

# TODO: rebase on project?


class Props(BaseModel):
    session: Optional[str]
    resource: dict


class Result(BaseModel):
    report: Dict


@router.post("/resource/validate")
def server_resource_validate(request: Request, props: Props) -> Result:
    project = request.app.get_project(props.session)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = resource.validate()
    return Result(report=report.to_descriptor())
