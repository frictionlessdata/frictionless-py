from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from typing import List
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from ... import helpers
from ... import types


class Props(BaseModel):
    path: str
    rows: List[types.IRow]
    tableSchema: types.IDescriptor  # TODO: rename to schema


class Result(BaseModel):
    path: str


@router.post("/text/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    # Forbid overwriting
    if props.path and helpers.test_file(project, path=props.path):
        raise FrictionlessException("file already exists")

    # Write contents
    path = helpers.write_table(
        project,
        path=props.path,
        rows=props.rows,
        schema=props.tableSchema,
    )

    return Result(path=path)
