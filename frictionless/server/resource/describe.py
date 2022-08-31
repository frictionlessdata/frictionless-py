from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..session import Session
from ..router import router


class ResourceDescribeProps(BaseModel):
    token: Optional[str]
    path: str


@router.post("/resource/describe")
def server_resource_describe(request: Request, props: ResourceDescribeProps):
    config = request.app.config
    session = Session(config, token=props.token)
    try:
        resource = Resource.from_descriptor(
            dict(path=props.path), basepath=session.basepath
        )
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    resource.infer()
    return dict(resource=resource.to_descriptor())
