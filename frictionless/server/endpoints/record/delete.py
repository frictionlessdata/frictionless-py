from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models
from . import read


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:  # type: ignore
    md = project.metadata
    db = project.database

    # Read record
    record = read.action(project, read.Props(path=props.path)).record

    # Delete table
    if record.type == "table":
        with db.engine.begin() as conn:
            table = db.metadata.tables[record.name]
            table.drop(conn)

    # Write record/report
    db.delete_artifact(name=record.name, type="report")
    md.delete_document(name=record.name, type="record")

    return Result(record=record)
