from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFieldItem
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    items: List[IFieldItem]


@router.post("/field/list")
def server_field_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    items = project.list_fields()
    return Result(items=items)
