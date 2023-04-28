from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
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
    sa = platform.sqlalchemy
    db = project.database

    record = db.select_record(props.path)
    assert record
    assert "tableName" in record
    table = db.metadata.tables[record["tableName"]]
    query = sa.select(table)
    if props.valid is not None:
        query = query.where(table.c._rowValid == props.valid)
    # TODO: recover (parameters have not been added)
    #  if limit:
    #  query = query.limit(limit)
    #  if offset:
    #  query = query.offset(offset)
    query = str(query)
    if props.order:
        query += f" ORDER BY {props.order}"
        if props.desc:
            query += " DESC"
    if props.limit:
        query += f" LIMIT {props.limit}"
        if props.offset:
            query += f" OFFSET {props.offset}"
    data = db.query(str(query))
    schema = record["resource"]["schema"]
    fdtable: ITable = {
        "tableSchema": schema,
        "header": data["header"],
        "rows": data["rows"],
    }

    return Result(table=fdtable)
