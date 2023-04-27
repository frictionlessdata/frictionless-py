from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    valid: Optional[bool]


class Result(BaseModel):
    count: int


@router.post("/table/count")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    count = project.database.count_table(props.path, valid=props.valid)
    return Result(count=count)
