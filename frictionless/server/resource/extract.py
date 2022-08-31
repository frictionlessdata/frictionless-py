from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..session import Session
from ..router import router
from ... import formats


# TODO: support limit/offset_rows


# TODO: encapsulate into extract (json-compat output)
SUPPORTED_TYPES = formats.JsonlParser.supported_types


class ResourceExtractProps(BaseModel):
    token: str
    resource: dict


@router.post("/resource/extract")
def server_resource_extract(request: Request, props: ResourceExtractProps):
    config = request.app.config
    session = Session(config, token=props.token)
    try:
        resource = Resource.from_descriptor(
            props.resource, basepath=session.public_basepath
        )
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    rows = resource.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    return dict(rows=rows)
