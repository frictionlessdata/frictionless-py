from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...detector import Detector
from ...resource import Resource
from ..router import router

# TODO: rebase on project?


class Props(BaseModel):
    session: Optional[str]
    path: str
    detector: Optional[dict]


class Result(BaseModel):
    resource: Dict


@router.post("/resource/describe")
def server_resource_describe(request: Request, props: Props) -> Result:
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
    return Result(resource=resource.to_descriptor())
