from typing import Optional
from pydantic import BaseModel
from fastapi import Request, Form
from ...project import Project
from ..router import router


# See the signature
class Props(BaseModel):
    pass


class Result(BaseModel):
    path: str


@router.post("/file/create")
async def server_file_create(
    request: Request,
    path: str,
    folder: Optional[str] = Form(None),
    session: Optional[str] = Form(None),
) -> Result:
    project: Project = request.app.get_project(session)
    path = project.create_file(path, folder=folder)
    return Result(path=path)
