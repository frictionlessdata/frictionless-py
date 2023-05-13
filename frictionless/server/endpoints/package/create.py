from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import Request
from ...project import Project
from ...router import router
from .. import json


class Props(BaseModel):
    path: Optional[str]
    package: Optional[Dict[str, Any]]
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/package/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = props.path or "datapackage.json"
    data = props.package or {"resources": []}
    result = json.write.action(
        project, json.write.Props(path=path, data=data, deduplicate=True)
    )

    return Result(path=result.path)
