from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....resource import Resource
from ...project import Project
from ...router import router
from ... import helpers
from ... import models
from ... import types


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record
    report: types.IDescriptor
    measure: models.Measure


@router.post("/file/sync")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Read record
    record = helpers.read_record_or_raise(project, path=props.path)

    # Index resource
    resource = Resource.from_descriptor(record.resource, basepath=str(fs.basepath))
    report = helpers.index_resource(project, resource=resource, table_name=record.name)

    # Create measure
    measure = models.Measure(
        errors=report.stats["errors"],
    )

    # Write record/report
    md.write_document(name=record.name, type="record", descriptor=record.dict())
    db.write_artifact(name=record.name, type="report", descriptor=report.to_descriptor())
    db.write_artifact(name=record.name, type="measure", descriptor=measure.dict())

    return Result(record=record, report=report.to_descriptor(), measure=measure)
