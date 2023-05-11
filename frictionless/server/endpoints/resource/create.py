from __future__ import annotations
from typing import Dict, Any, List
from pydantic import BaseModel
from fastapi import Request
from datetime import datetime
from ....platform import platform
from ....resource import Resource
from ...project import Project
from ...router import router
from ... import settings
from ... import helpers
from . import map


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    resource: Dict[str, Any]


@router.post("/resource/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: raise if already exist?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata

    # Describe resource
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    resource.infer()

    # Get resource id
    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    # TODO: rebase on direct metadata?
    result = map.action(project)
    for item in result.items.values():
        ids.append(item["id"])
        if item["path"] == resource.path:
            id = item["id"]
            found = True
    if not found:
        suffix = 1
        while id in ids:
            id = template % suffix
            suffix += 1

    # Add custom fields to resource
    resource.custom["id"] = id
    resource.custom["datatype"] = resource.datatype

    return Result(resource=resource.to_descriptor())
