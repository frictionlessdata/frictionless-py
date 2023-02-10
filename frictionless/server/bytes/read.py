from typing import Optional
from pydantic import BaseModel
from fastapi import Request, Response
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    pass


@router.post("/bytes/read")
def server_bytes_read(request: Request, props: Props) -> Response:
    project: Project = request.app.get_project(props.session)
    bytes = project.read_bytes(props.path)
    return Response(bytes, media_type="application/octet-stream")
