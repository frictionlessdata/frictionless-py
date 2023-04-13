from pydantic import BaseModel
from fastapi import Request
from ...project import Project, ITable
from ...router import router


class Props(BaseModel):
    query: str


class Result(BaseModel):
    table: ITable


@router.post("/table/query")
def server_table_query(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    table = project.query_table(props.query)
    return Result(table=table)
