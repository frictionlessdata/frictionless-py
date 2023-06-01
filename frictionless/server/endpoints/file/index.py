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


@router.post("/file/index")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    from ... import endpoints

    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Return existent (we check if report is present; if not we do sync)
    record = helpers.read_record(project, path=props.path)
    if record:
        table = db.get_table(name=record.name)
        report = db.read_artifact(name=record.name, type="report")
        measure = helpers.read_measure(project, path=props.path)
        if (
            report is None
            or measure is None
            or (record.type == "table" and table is None)
        ):
            result = endpoints.file.sync.action(
                project, endpoints.file.sync.Props(path=props.path)
            )
            record = result.record
            report = result.report
            measure = result.measure
        return Result(record=record, report=report, measure=measure)

    # Index resource
    path, basepath = fs.get_path_and_basepath(props.path)
    name = helpers.name_record(project, path=path)
    resource = Resource(path=path, basepath=basepath)
    report = helpers.index_resource(project, resource=resource, table_name=name)

    # Create measure
    measure = models.Measure(
        errors=report.stats["errors"],
    )

    # Create record
    record = models.Record(
        name=name,
        path=props.path,
        type=resource.datatype,
        resource=resource.to_descriptor(),
    )

    # Write document/artifacts
    md.write_document(name=record.name, type="record", descriptor=record.dict())
    db.write_artifact(name=record.name, type="report", descriptor=report.to_descriptor())
    db.write_artifact(name=record.name, type="measure", descriptor=measure.dict())

    return Result(record=record, report=report.to_descriptor(), measure=measure)
