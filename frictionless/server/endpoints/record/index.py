from __future__ import annotations
import re
import stringcase  # type: ignore
from slugify.slugify import slugify
from typing import List
from tinydb import Query
from pydantic import BaseModel
from fastapi import Request
from ....resources import TableResource
from ....resource import Resource
from ....indexer import Indexer
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel, extra="forbid"):
    path: str
    sync: bool


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
    name = make_unique_name(project, resource)

    # Index resource
    report = None
    if isinstance(resource, TableResource):
        indexer = Indexer(
            resource=resource,
            database=db.engine,
            table_name=name,
            with_metadata=True,
        )
        report = indexer.index()
    if not report:
        report = resource.validate()

    # Create record
    record = models.Record(
        name=name,
        path=props.path,
        type=resource.datatype,
        stats=models.Stats(errors=report.stats["errors"]),
        resource=resource.to_descriptor(),
    )

    # Write record/report
    md.write_document(name=name, type="record", descriptor=record.dict())
    db.write_artifact(name=name, type="report", descriptor=report.to_descriptor())

    return Result(record=record)


def make_unique_name(project: Project, resource: Resource) -> str:
    md = project.metadata

    name = slugify(resource.name)
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    name = stringcase.camelcase(name)  # type: ignore

    names: List[str] = []
    found = False
    template = f"{name}%s"
    for item in md.iter_documents(type="record"):
        item_name: str = item["name"]
        names.append(item_name)
        if item["path"] == resource.path:
            name = item_name
            found = True
    if not found:
        suffix = 1
        while name in names:
            name = template % suffix
            suffix += 1

    return name
