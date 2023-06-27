from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ... import helpers, types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    toPath: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/file/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    from ... import endpoints

    # Copy contents
    if props.toPath:
        endpoints.file.copy.action(
            project, endpoints.file.copy.Props(path=props.path, toPath=props.toPath)
        )

    # Patch record
    record = helpers.patch_record(
        project,
        path=props.path,
        toPath=props.toPath,
        resource=props.resource,
    )

    return Result(path=record.path)
