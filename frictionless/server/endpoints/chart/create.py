from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router
from ..json import write as json_write
from ... import types


class Props(BaseModel):
    path: Optional[str] = None
    chart: Optional[types.IChart] = None


class Result(BaseModel):
    path: str


@router.post("/chart/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = props.path or "chart.json"
    data = props.chart or {"encoding": {}}
    result = json_write.action(
        project, json_write.Props(path=path, data=data, deduplicate=True)
    )

    return Result(path=result.path)
