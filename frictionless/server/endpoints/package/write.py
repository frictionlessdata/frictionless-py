from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    data: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/package/write")
def server_package_write(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    project.write_package(props.path, data=props.data)
    return Result(path=props.path)
