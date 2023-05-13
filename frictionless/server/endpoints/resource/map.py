from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel, extra="forbid"):
    pass


class Result(BaseModel, extra="forbid"):
    items: Dict[str, models.ResourceItem]


@router.post("/resource/map")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Optional[Props] = None) -> Result:
    md = project.metadata
    db = project.database

    # Map errors
    errors: Dict[str, int] = {}
    for id, descriptor in db.iter_artifacts(type="stats"):
        errors[id] = descriptor["errors"]

    # Map resources
    result = Result(items={})
    for descriptor in md.iter_documents(type="resource"):
        item = models.ResourceItem(
            id=descriptor["id"],
            path=descriptor["path"],
            datatype=descriptor["datatype"],
        )
        item.errors = errors.get(item.id, None)
        result.items[item.path] = item

    return result
