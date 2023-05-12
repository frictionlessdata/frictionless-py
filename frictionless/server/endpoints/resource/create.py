from __future__ import annotations
from typing import Dict, Any, List, TYPE_CHECKING
from tinydb import Query
from pydantic import BaseModel
from fastapi import Request
from datetime import datetime
from ....exception import FrictionlessException
from ....platform import platform
from ....resource import Resource
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor
from ... import helpers
from ...interfaces import IDescriptor


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
    md = project.metadata

    # Check existence
    if md.resources.get(Query().path == props.path):
        raise FrictionlessException("Resource already exists")

    # Infer resource
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    resource.infer()

    # Extend resource
    id = make_unique_id(project, resource)
    resource.custom["id"] = id
    resource.custom["datatype"] = resource.datatype

    # Write resource
    descriptor = resource.to_descriptor()
    md.resources.insert(md.document(id, **descriptor))  # type: ignore
    return Result(resource=descriptor)


# Internal


def make_unique_id(project: Project, resource: Resource) -> str:
    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    for item in project.metadata.resources:
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
