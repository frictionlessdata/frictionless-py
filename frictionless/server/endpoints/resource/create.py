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
from ...interfaces import IDescriptor
from ... import helpers


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    resource: IDescriptor


@router.post("/resource/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: raise if already exist?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database
    md = project.metadata

    # Check existence
    if md.resources.get(Query().path == props.path):
        raise FrictionlessException("Resource already exists")

    # Create resource
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
    print(report)

    # Extend resource
    resource.custom["id"] = id
    resource.custom["datatype"] = resource.datatype

    # Write resource
    descriptor = resource.to_descriptor()
    md.resources.insert(md.document(id, **descriptor))  # type: ignore
    return Result(resource=descriptor)


def make_unique_id(project: Project, resource: Resource) -> str:
    md = project.metadata

    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    for item in md.resources:
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
