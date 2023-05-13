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
    db = project.database

    # Prepare errors
    errors: Dict[str, int] = {}
    for id, descriptor in db.iter_artifacts(type="stats"):
        errors[id] = descriptor["errors"]

    result = Result(items={})
    for descriptor in md.iter_documents(type="resource"):
        id: str = descriptor["id"]
        path: str = descriptor["path"]
        result.items[path] = {
            "id": id,
            "path": path,
            "datatype": descriptor["datatype"],
        }
        if id in errors:
            result.items[path]["errorCount"] = errors[id]

    return result
