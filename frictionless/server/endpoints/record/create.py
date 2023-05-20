from __future__ import annotations
from typing import List
from tinydb import Query
from pydantic import BaseModel
from fastapi import Request
from ....resources import TableResource
from ....resource import Resource
from ....indexer import Indexer
from ...project import Project
from ...router import router
from ... import helpers
from ... import models


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Return existent
    # TODO: ensure resource is fully indexed (table/report)
    descriptor = md.find_document(type="record", query=Query().path == props.path)
    if descriptor:
        record = models.Record.parse_obj(descriptor)
        return Result(record=record)

    # Prepare resource
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    id = make_unique_id(project, resource)

    # Index resource
    report = None
    if isinstance(resource, TableResource):
        indexer = Indexer(
            resource=resource,
            database=db.engine,
            table_name=id,
            with_metadata=True,
        )
        report = indexer.index()
    if not report:
        report = resource.validate()

    # Create record
    record = models.Record(
        id=id,
        path=props.path,
        type=resource.datatype,
        stats=models.Stats(errors=report.stats["errors"]),
        resource=resource.to_descriptor(),
    )

    # Write record/report
    md.write_document(id=id, type="record", descriptor=record.dict())
    db.write_artifact(id=id, type="report", descriptor=report.to_descriptor())

    return Result(record=record)


def make_unique_id(project: Project, resource: Resource) -> str:
    md = project.metadata

    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    for item in md.iter_documents(type="record"):
        item_id: str = item["id"]
        ids.append(item_id)
        if item["path"] == resource.path:
            id = item_id
            found = True
    if not found:
        suffix = 1
        while id in ids:
            id = template % suffix
            suffix += 1

    return id
