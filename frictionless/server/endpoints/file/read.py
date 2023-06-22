from __future__ import annotations

from typing import Optional

from fastapi import Request, Response
from pydantic import BaseModel

from ....exception import FrictionlessException
from ....resources import FileResource
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    size: Optional[int]


class Result(BaseModel, extra="forbid"):
    bytes: bytes


@router.post("/file/read")
def server_file_read(request: Request, props: Props) -> Response:
    result = action(request.app.get_project(), props)
    return Response(result.bytes, media_type="application/octet-stream")


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Source
    source = fs.get_fullpath(props.path)
    if not source.is_file():
        raise FrictionlessException("file does not exist")

    # Bytes
    resource = FileResource(path=str(source))
    bytes = resource.read_file(size=props.size)

    return Result(bytes=bytes)
