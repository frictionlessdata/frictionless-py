from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project, IChart
from ...router import router


class Props(BaseModel):
    path: Optional[str]
    chart: Optional[IChart]


class Result(BaseModel):
    path: str


def chart_create(project: Project, props: Props) -> Result:
    path = props.path or "chart.json"
    data = props.chart or {"encoding": {}}
    path = project.get_secure_fullpath(path, deduplicate=True)
    project.filesystem.write_json(path, data=data)
    path = project.get_secure_relpath(path)
    return Result(path=path)


@router.post("/chart/create")
def server_chart_create(request: Request, props: Props) -> Result:
    return chart_create(request.app.get_project(), props)
