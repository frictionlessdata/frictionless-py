from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ..exception import FrictionlessException
from ..resource import Resource
from .server import server
from .. import formats


# TODO: encapsulate into extract (json-compat output)
SUPPORTED_TYPES = formats.JsonlParser.supported_types


class TransformPayload(BaseModel):
    resource: dict


@server.post("/transform")
def server_transform(payload: TransformPayload):
    try:
        source = Resource.from_descriptor(payload.resource)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    target = source.transform()
    rows = target.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    # TODO: improve output resource (remove pipeline/etc)?
    return dict(resource=target.to_descriptor(), rows=rows)
