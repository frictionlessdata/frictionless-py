from __future__ import annotations

from typing import List, Optional

from fastapi import Request
from pydantic import BaseModel

from ... import helpers, types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    rows: List[types.IRow]
    tableSchema: types.IDescriptor  # TODO: rename to schema
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/table/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = helpers.write_table(
        project,
        path=props.path,
        rows=props.rows,
        schema=props.tableSchema,
        deduplicate=props.deduplicate,
    )
    return Result(path=path)
