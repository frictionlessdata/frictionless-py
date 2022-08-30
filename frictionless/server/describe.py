from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ..exception import FrictionlessException
from ..resource import Resource
from .server import server


class DescribePayload(BaseModel):
    path: str


@server.post("/describe")
def server_describe(payload: DescribePayload):
    try:
        resource = Resource.from_descriptor(dict(path=payload.path))
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    resource.infer()
    return dict(resource=resource.to_descriptor())
