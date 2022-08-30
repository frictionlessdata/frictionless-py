from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ..exception import FrictionlessException
from ..resource import Resource
from .server import server
from .. import formats


# TODO: encapsulate into extract (json-compat output)
SUPPORTED_TYPES = formats.JsonlParser.supported_types


class ValidatePayload(BaseModel):
    resource: dict


@server.post("/extract")
def server_extract(payload: ValidatePayload):
    try:
        resource = Resource.from_descriptor(payload.resource)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    rows = resource.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    return dict(rows=rows)
