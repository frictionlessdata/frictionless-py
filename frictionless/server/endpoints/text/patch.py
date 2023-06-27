from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ... import helpers, types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    text: Optional[str]
    toPath: Optional[str]
    resource: Optional[types.IDescriptor]


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/text/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Forbid overwriting for export
    if props.toPath and helpers.test_file(project, path=props.toPath):
        raise FrictionlessException("file already exists")

    # Patch record
    record = helpers.patch_record(
        project,
        path=props.path,
        toPath=props.toPath,
        resource=props.resource,
        isDataChanged=props.text is not None,
    )

    # Write contents
    if props.text is not None:
        helpers.write_text(project, path=record.path, text=props.text, overwrite=True)

    return Result(path=record.path)
