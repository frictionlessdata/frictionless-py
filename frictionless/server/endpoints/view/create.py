from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router
from .. import json
from ... import types


class Props(BaseModel):
    path: Optional[str] = None
    view: Optional[types.IView] = None


class Result(BaseModel):
    path: str


@router.post("/view/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: reuse view.write?
def action(project: Project, props: Props) -> Result:
    path = props.path or "view.json"
    data = props.view or {"query": ""}
    result = json.write.action(
        project, json.write.Props(path=path, data=data, deduplicate=True)
    )

    return Result(path=result.path)
