from __future__ import annotations
from tinydb import Query
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from .. import json


class Props(BaseModel):
    path: str
    data: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/metadata/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    # Delete metadata
    resource = md.find_document(type="resource", query=Query().path == props.path)
    if resource:
        md.delete_document(id=resource["id"], type="resource")

    # Write data
    result = json.write.action(
        project, json.write.Props(path=props.path, data=props.data)
    )

    return Result(path=result.path)
