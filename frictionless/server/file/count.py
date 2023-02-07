from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    count: int


@router.post("/file/count")
def server_file_count(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    count = project.count_files()
    return Result(count=count)
