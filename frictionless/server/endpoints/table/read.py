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


class Result(BaseModel):
    table: ITable


@router.post("/table/read")
def server_table_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    table = project.read_table(
        props.path,
        valid=props.valid,
        limit=props.limit,
        offset=props.offset,
    )
    return Result(table=table)
