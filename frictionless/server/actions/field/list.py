from typing import List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFieldItem
from ...router import router


class Props(BaseModel):
    pass


class Result(BaseModel):
    items: List[IFieldItem]


@router.post("/field/list")
def server_field_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    items = project.list_fields()
    return Result(items=items)
