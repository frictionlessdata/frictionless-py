from typing import Optional, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    data: Any


@router.post("/json/read")
def server_json_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    data = project.read_json(props.path)
    return Result(data=data)
