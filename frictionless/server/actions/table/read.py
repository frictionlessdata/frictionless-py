from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, ITable
from ...router import router


class Props(BaseModel):
    path: str
    valid: Optional[bool]
    limit: Optional[int]
    offset: Optional[int]
    order: Optional[str]
    desc: Optional[bool]


class Result(BaseModel):
    table: ITable


@router.post("/table/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    table = project.database.read_table(
        props.path,
        valid=props.valid,
        limit=props.limit,
        offset=props.offset,
        order=props.order,
        desc=props.desc,
    )
    return Result(table=table)
