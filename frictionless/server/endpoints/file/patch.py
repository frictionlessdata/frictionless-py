from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import helpers
from ... import types


class Props(BaseModel):
    path: str
    bytes: Optional[bytes] = None
    toPath: Optional[str] = None
    resource: Optional[types.IDescriptor] = None


class Result(BaseModel):
    path: str


@router.post("/file/patch")
async def endpoint(
    request: Request,
    file: UploadFile = File(),
    path: str = Form(),
    toPath: Optional[str] = Form(None),
    resource: Optional[types.IDescriptor] = Form(None),
) -> Result:
    bytes = await file.read()
    return action(
        request.app.get_project(),
        Props(path=path, bytes=bytes, toPath=toPath, resource=resource),
    )


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
        isDataChanged=props.bytes is not None,
    )

    # Write contents
    if props.bytes is not None:
        helpers.write_file(project, path=record.path, bytes=props.bytes)

    return Result(path=record.path)
