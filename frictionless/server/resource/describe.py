from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...detector import Detector
from ...resource import Resource
from ..router import router


class ResourceDescribeProps(BaseModel):
    session: Optional[str]
    path: str
    detector: Optional[dict]


@router.post("/resource/describe")
def server_resource_describe(request: Request, props: ResourceDescribeProps):
    project = request.app.get_project(props.session)
    try:
        detector = Detector.from_descriptor(props.detector) if props.detector else None
        resource = Resource.from_descriptor(
            dict(path=props.path), basepath=project.basepath, detector=detector
        )
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    resource.infer()
    return dict(resource=resource.to_descriptor())
