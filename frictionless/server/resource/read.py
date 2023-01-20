from __future__ import annotations
import base64
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..router import router


class ProjectReadProps(BaseModel):
    session: Optional[str]
    resource: dict


@router.post("/resource/read-bytes")
def server_resource_read_bytes(request: Request, props: ProjectReadProps):
    project = request.app.get_project(props.session)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    # TODO: fix size limit in the resource
    bytes = resource.read_bytes(size=1000000)
    return dict(bytes=base64.b64encode(bytes))


@router.post("/resource/read-text")
def server_resource_read_text(request: Request, props: ProjectReadProps):
    project = request.app.get_project(props.session)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    text = resource.read_text()
    return dict(text=text)


@router.post("/resource/read-data")
def server_resource_read_data(request: Request, props: ProjectReadProps):
    project = request.app.get_project(props.session)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    data = resource.read_data()
    return dict(data=data)
