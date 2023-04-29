from pathlib import Path
from typing import Optional
from fastapi import Request
from pydantic import BaseModel
from urllib.parse import urlparse
from ....resources import FileResource
from ...project import Project
from ...router import router
from .. import file


class Props(BaseModel):
    url: str
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/link/fetch")
def server_file_read(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Path
    parsed = urlparse(props.url)
    path = Path(parsed.path).name or "name"

    # Bytes
    resource = FileResource(path=props.url)
    bytes = resource.read_file()

    # Create
    result = file.create.action(
        project,
        file.create.Props(
            path=path, bytes=bytes, folder=props.folder, deduplicate=props.deduplicate
        ),
    )

    return Result(path=result.path)
