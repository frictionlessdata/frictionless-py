from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, ITable
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    valid: Optional[bool]
    limit: Optional[int]
    offset: Optional[int]


class Result(BaseModel):
    table: ITable


# TODO: move to table folder?
@router.post("/file/read-table")
def server_file_read_table(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    table = project.read_file_table(
        props.path,
        valid=props.valid,
        limit=props.limit,
        offset=props.offset,
    )
    return Result(table=table)
