from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ..exception import FrictionlessException
from ..resource import Resource
from .server import server


class ValidatePayload(BaseModel):
    resource: dict


@server.post("/validate")
def server_validate(payload: ValidatePayload):
    try:
        resource = Resource.from_descriptor(payload.resource)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = resource.validate()
    return dict(report=report.to_descriptor())
