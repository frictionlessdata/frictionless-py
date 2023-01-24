from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import Request, HTTPException
from ...exception import FrictionlessException
from ...resource import Resource
from ...project import Project
from ..router import router
from ... import formats

# TODO: rebase on project?
# TODO: support limit/offset_rows
# TODO: encapsulate into extract (json-compat output)

SUPPORTED_TYPES = formats.JsonlParser.supported_types


class Props(BaseModel):
    session: Optional[str]
    resource: dict


class Result(BaseModel):
    table: Dict


@router.post("/resource/extract")
def server_resource_extract(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
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
    return Result(table=table)
