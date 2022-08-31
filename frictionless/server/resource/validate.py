from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..session import Session
from ..router import router


class ResourceValidateProps(BaseModel):
    token: str
    resource: dict


@router.post("/resource/validate")
def server_resource_validate(request: Request, props: ResourceValidateProps):
    config = request.app.config
    session = Session(config, token=props.token)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=session.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = resource.validate()
    return dict(report=report.to_descriptor())
