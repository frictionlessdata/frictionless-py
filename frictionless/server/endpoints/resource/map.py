from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ...interfaces import IResourceItem


class Props(BaseModel, extra="forbid"):
    pass


class Result(BaseModel, extra="forbid"):
    items: Dict[str, IResourceItem]


@router.post("/resource/map")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Optional[Props] = None) -> Result:
    md = project.metadata

    metadata = md.read()
    result = Result(items={})
    for resource in metadata.values():
        id = resource["id"]
        path = resource["path"]
        result.items[path] = {"id": id, "path": path}

    return result
