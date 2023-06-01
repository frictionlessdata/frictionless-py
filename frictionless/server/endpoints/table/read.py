from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ...project import Project
from ...router import router
from ... import helpers
from ... import types


class Props(BaseModel):
    path: str
    valid: Optional[bool]
    limit: Optional[int]
    offset: Optional[int]
    order: Optional[str]
    desc: Optional[bool]


class Result(BaseModel):
    rows: List[types.IRow]


@router.post("/table/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database
    sa = platform.sqlalchemy

    record = helpers.read_record_or_raise(project, path=props.path)
    table = db.metadata.tables[record.name]
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

    result = db.query(str(query))
    rows = list(dict(item) for item in result.mappings())
    return Result(rows=rows)
