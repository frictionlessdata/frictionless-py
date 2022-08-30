from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..server import server


class ResourceValidatePayload(BaseModel):
    resource: dict


@server.post("/resource/validate")
def server_resource_validate(payload: ResourceValidatePayload):
    try:
        resource = Resource.from_descriptor(payload.resource)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = resource.validate()
    return dict(report=report.to_descriptor())
