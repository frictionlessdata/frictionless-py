from typing import Any, Dict
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class props(BaseModel):
    path: str
    control: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/package/publish")
def server_package_publish(request: Request, props: props) -> Result:
    project: Project = request.app.get_project()
    path = project.publish_package(props.path, control=props.control)
    return Result(path=path)
