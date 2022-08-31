from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..router import router


class ResourceValidateProps(BaseModel):
    resource: dict


@router.post("/resource/validate")
def server_resource_validate(props: ResourceValidateProps):
    try:
        resource = Resource.from_descriptor(props.resource)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = resource.validate()
    return dict(report=report.to_descriptor())
