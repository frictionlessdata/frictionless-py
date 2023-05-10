from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ...interfaces import IResourceItem


class Props(BaseModel, extra="forbid"):
    pass


class Result(BaseModel, extra="forbid"):
    items: List[IResourceItem]


@router.post("/resource/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: implement actual logic
def action(project: Project, props: Optional[Props] = None) -> Result:
    return Result(
        items=[
            {"id": "id", "path": "path"},
        ]
    )
