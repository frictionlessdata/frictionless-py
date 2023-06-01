from __future__ import annotations
from fastapi import Request
from pydantic import BaseModel
from typing import Optional
from ....formats.sql import SqlControl
from ....resources import TableResource
from ....exception import FrictionlessException
from ....platform import platform
from ...project import Project
from ...router import router
from ... import helpers
from ... import models
from ... import types


class Props(BaseModel):
    path: str
    toPath: Optional[str]
    history: Optional[models.History]
    resource: Optional[types.IDescriptor]


class Result(BaseModel):
    path: str


@router.post("/table/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database
    sa = platform.sqlalchemy

    # Forbid overwriting
    if props.toPath and helpers.test_file(project, path=props.toPath):
        raise FrictionlessException("file already exists")

    # Patch record
    record = helpers.patch_record(
        project,
        path=props.path,
        toPath=props.toPath,
        resource=props.resource,
    )

    # Write history
    if props.history:
        # Patch database table
        with db.engine.begin() as conn:
            table = db.metadata.tables[record.name]
            for change in props.history.changes:
                if change.type == "cell-update":
                    conn.execute(
                        sa.update(table)
                        .where(table.c._rowNumber == change.rowNumber)
                        .values(**{change.fieldName: change.value})
                    )

        # Export database table
        target = fs.get_fullpath(props.toPath or props.path)
        control = SqlControl(table=record.name, with_metadata=True)
        resource = TableResource(path=db.database_url, control=control)
        resource.write_table(path=str(target))

    # Delete report
    if props.history is not None and not props.toPath:
        db.delete_artifact(name=record.name, type="report")

    return Result(path=record.path)
