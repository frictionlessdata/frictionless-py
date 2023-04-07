from typing import Optional, Any, Dict
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class props(BaseModel):
    session: Optional[str]
    path: str
    control: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/package/publish")
def server_package_publish(request: Request, props: props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.publish_package(props.path, control=props.control)
    return Result(path=path)
