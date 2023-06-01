from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....resource import Resource
from ...project import Project
from ...router import router
from . import sync as file_sync
from ... import helpers
from ... import models
from ... import types


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record
    report: types.IDescriptor


@router.post("/file/index")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Return existent (we check if report is present; if not we do sync)
    record = helpers.read_record(project, path=props.path)
    if record:
        table = db.get_table(name=record.name)
        report = db.read_artifact(name=record.name, type="report")
        if report is None or (record.type == "table" and table is None):
            result = file_sync.action(project, file_sync.Props(path=props.path))
            record = result.record
            report = result.report
        return Result(record=record, report=report)

    # Index resource
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    record_name = helpers.make_record_name(project, resource=resource)
    report = helpers.index_resource(project, resource=resource, table_name=record_name)

    # Create record
    record = models.Record(
        name=record_name,
        path=props.path,
        type=resource.datatype,
        stats=models.Stats(errors=report.stats["errors"]),
        resource=resource.to_descriptor(),
    )

    # Write record/report
    md.write_document(name=record_name, type="record", descriptor=record.dict())
    db.write_artifact(name=record_name, type="report", descriptor=report.to_descriptor())

    return Result(record=record, report=report.to_descriptor())
