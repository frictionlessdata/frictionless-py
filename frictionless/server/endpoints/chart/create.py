from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...interfaces import IChart
from ...project import Project
from ...router import router
from .. import json


class Props(BaseModel):
    path: Optional[str] = None
    chart: Optional[IChart] = None


class Result(BaseModel):
    path: str


# TODO: move to write?
@router.post("/chart/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = props.path or "chart.json"
    data = props.chart or {"encoding": {}}
    result = json.write.action(
        project, json.write.Props(path=path, data=data, deduplicate=True)
    )

    return Result(path=result.path)
