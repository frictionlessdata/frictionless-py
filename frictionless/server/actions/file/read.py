from pydantic import BaseModel
from fastapi import Request, Response
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    pass


@router.post("/file/read")
def server_file_read(request: Request, props: Props) -> Response:
    project: Project = request.app.get_project()
    bytes = project.read_file(props.path)
    return Response(bytes, media_type="application/octet-stream")
