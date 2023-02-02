from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IResourceListItem
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    items: List[IResourceListItem]


@router.post("/resource/list")
def server_resource_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    items = project.resource_list()
    return Result(items=items)
