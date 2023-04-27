from pydantic import BaseModel
from fastapi import Request
from ...project import Project, ITable
from ...router import router


class Props(BaseModel):
    query: str


class Result(BaseModel):
    table: ITable


@router.post("/table/query")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    table = project.database.query_table(props.query)
    return Result(table=table)
