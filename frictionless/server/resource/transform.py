from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ..router import router
from ... import formats

# TODO: rebase on project?
# TODO: encapsulate into extract (json-compat output)

SUPPORTED_TYPES = formats.JsonlParser.supported_types


class Props(BaseModel):
    session: Optional[str]
    resource: dict


class Result(BaseModel):
    resource: Dict
    table: Dict


@router.post("/resource/transform")
def server_resource_transform(request: Request, props: Props) -> Result:
    project = request.app.get_project(props.session)
    try:
        source = Resource.from_descriptor(props.resource, basepath=project.basepath)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    # TODO: handle errors
    target = source.transform()
    rows = target.extract(process=lambda row: row.to_dict(types=SUPPORTED_TYPES))
    table = dict(header=target.header, rows=rows)
    # TODO: improve output resource (remove pipeline/etc)?
    return Result(resource=target.to_descriptor(), table=table)
