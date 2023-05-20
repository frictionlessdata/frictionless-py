from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....schema import Schema
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel):
    query: str


class Result(BaseModel):
    table: models.Table


@router.post("/table/query")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database

    result = db.query(props.query)
    rows = list(dict(item) for item in result.mappings())
    header = list(result.keys())
    schema = Schema.describe(rows).to_descriptor()
    table = models.Table(tableSchema=schema, header=header, rows=rows)

    return Result(table=table)
