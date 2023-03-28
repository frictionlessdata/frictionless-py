from typing import Optional, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    data: Any


class Result(BaseModel):
    path: str


@router.post("/json/write")
def server_json_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.write_json(props.path, data=props.data)
    return Result(path=props.path)
