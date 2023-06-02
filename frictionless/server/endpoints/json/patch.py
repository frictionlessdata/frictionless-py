from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import helpers
from ... import types


class Props(BaseModel):
    path: str
    data: Optional[Any] = None
    toPath: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel):
    path: str


@router.post("/metadata/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = props.toPath or props.path

    # Forbid overwriting
    if props.toPath and helpers.test_file(project, path=props.toPath):
        raise FrictionlessException("file already exists")

    # Patch record
    helpers.patch_record(
        project,
        path=props.path,
        toPath=props.toPath,
        resource=props.resource,
        isDataChanged=props.data is not None,
    )

    # Write contents
    if props.data is not None:
        helpers.write_json(project, path=path, data=props.data)

    return Result(path=path)
