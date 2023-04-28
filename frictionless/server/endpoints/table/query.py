from pydantic import BaseModel
from fastapi import Request
from ....schema import Schema
from ...project import Project
from ...interfaces import ITable
from ...router import router


class Props(BaseModel):
    query: str


class Result(BaseModel):
    table: ITable


@router.post("/table/query")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database

    result = db.query(props.query)
    schema = Schema.describe(result["rows"]).to_descriptor()
    table: ITable = {
        "tableSchema": schema,
        "header": result["header"],
        "rows": result["rows"],
    }

    return Result(table=table)
