from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import Request
from pydantic import BaseModel

from ....resources import FileResource
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    url: str
    path: Optional[str] = None
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/file/fetch")
def server_file_read(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    from ... import endpoints

    # Load
    resource = FileResource(path=props.url)
    bytes = resource.read_file()

    # Save
    parsed = urlparse(props.url)
    path = props.path or Path(parsed.path).name or "link"
    result = endpoints.file.create.action(
        project,
        endpoints.file.create.Props(
            path=path,
            bytes=bytes,
            folder=props.folder,
            deduplicate=props.deduplicate,
        ),
    )

    return Result(path=result.path)
