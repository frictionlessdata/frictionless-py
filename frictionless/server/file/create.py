from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


# See the signature
class Props(BaseModel):
    path: str
    session: Optional[str]
    folder: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/file/create")
async def server_file_create(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.create_file(props.path, folder=props.folder)
    return Result(path=path)
