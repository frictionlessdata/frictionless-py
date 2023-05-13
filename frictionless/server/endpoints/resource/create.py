from __future__ import annotations
from typing import List
from tinydb import Query
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ....resources import TableResource
from ....resource import Resource
from ....indexer import Indexer
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor
from ... import helpers


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    resource: IDescriptor


@router.post("/resource/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Prepare resource
    if md.find_document(type="resource", query=Query().path == props.path):
        raise FrictionlessException("Resource already exists")
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    id = make_unique_id(project, resource)

    # Index resource
    if not isinstance(resource, TableResource):
        report = resource.validate()
    else:
        report = Indexer(
            resource=resource,
            database=db.engine,
            table_name=id,
            with_metadata=True,
        ).index()

    # Write metadata
    descriptor = resource.to_descriptor()
    descriptor["id"] = id
    descriptor["datatype"] = resource.datatype
    md.write_document(id=id, type="resource", descriptor=descriptor)

    # Write artifacts
    if report:
        stats = dict(errors=report.stats["errors"])
        db.write_artifact(id=id, type="stats", descriptor=stats)
        db.write_artifact(id=id, type="report", descriptor=report.to_descriptor())

    return Result(resource=descriptor)


def make_unique_id(project: Project, resource: Resource) -> str:
    md = project.metadata

    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    for item in md.iter_documents(type="resource"):
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
