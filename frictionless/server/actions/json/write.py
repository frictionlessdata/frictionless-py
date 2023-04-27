from typing import Any, Optional
from pydantic import BaseModel
from fastapi import Request
from ....resources import JsonResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    data: Any
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/json/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fullpath = project.get_secure_fullpath(props.path, deduplicate=props.deduplicate)
    resource = JsonResource(data=props.data)
    resource.write_json(path=fullpath)
    path = project.get_secure_relpath(fullpath)
    return Result(path=path)
