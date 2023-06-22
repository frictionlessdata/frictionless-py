from __future__ import annotations

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ....formats.sql import SqlControl
from ....platform import platform
from ....resources import TableResource
from ... import helpers, models, types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    toPath: Optional[str]
    history: Optional[models.History]
    resource: Optional[types.IDescriptor]


class Result(BaseModel, extra="forbid"):
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
        isDataChanged=props.history is not None,
    )

    # Copy table
    if props.toPath:
        fromRecord = helpers.read_record_or_raise(project, path=props.path)
        with db.engine.begin() as conn:
            query = f'CREATE TABLE "{record.name}" AS SELECT * FROM "{fromRecord.name}"'
            conn.execute(sa.text(query))
            db.metadata.reflect(conn, views=True)

    # Patch table
    if props.history:
        table = db.metadata.tables[record.name]

        # Patch database table
        with db.engine.begin() as conn:
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

    return Result(path=record.path)
