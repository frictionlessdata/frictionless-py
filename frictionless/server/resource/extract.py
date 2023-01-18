from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..router import router
from ... import formats


# TODO: support limit/offset_rows


# TODO: encapsulate into extract (json-compat output)
SUPPORTED_TYPES = formats.JsonlParser.supported_types


class ResourceExtractProps(BaseModel):
    session: Optional[str]
    resource: dict


@router.post("/resource/extract")
def server_resource_extract(request: Request, props: ResourceExtractProps):
    project = request.app.get_project(props.session)
    try:
        resource = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    rows = resource.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    table = dict(
        schema=resource.schema.to_descriptor(),
        header=resource.header.to_list(),
        rows=rows,
    )
    return dict(table=table)
