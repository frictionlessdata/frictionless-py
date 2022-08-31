from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..session import Session
from ..router import router
from ... import formats


# TODO: encapsulate into extract (json-compat output)
SUPPORTED_TYPES = formats.JsonlParser.supported_types


class ResourceTransformProps(BaseModel):
    token: str
    resource: dict


@router.post("/resource/transform")
def server_resource_transform(request: Request, props: ResourceTransformProps):
    config = request.app.config
    session = Session(config, token=props.token)
    try:
        source = Resource.from_descriptor(
            props.resource, basepath=session.public_basepath
        )
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    target = source.transform()
    rows = target.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    # TODO: improve output resource (remove pipeline/etc)?
    return dict(resource=target.to_descriptor(), rows=rows)
