from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ... import helpers, types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    data: Optional[Any] = None
    toPath: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/json/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Forbid overwriting
    if props.toPath and helpers.test_file(project, path=props.toPath):
        raise FrictionlessException("file already exists")

    # Patch record
    record = helpers.patch_record(
        project,
        path=props.path,
        toPath=props.toPath,
        resource=props.resource,
        isDataChanged=props.data is not None,
    )

    # Write contents
    if props.data is not None:
        helpers.write_json(project, path=record.path, data=props.data, overwrite=True)

    return Result(path=record.path)
