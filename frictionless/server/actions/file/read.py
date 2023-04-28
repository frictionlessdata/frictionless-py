from pydantic import BaseModel
from fastapi import Request, Response
from ....resources import FileResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    bytes: bytes


@router.post("/file/read")
def server_file_read(request: Request, props: Props) -> Response:
    result = action(request.app.get_project(), props)
    return Response(result.bytes, media_type="application/octet-stream")


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_secure_fullpath(props.path)
    assert fs.is_file(fullpath)
    resource = FileResource(path=fullpath)
    bytes = resource.read_file()

    return Result(bytes=bytes)
