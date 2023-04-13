from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IChart
from ...router import router
from .endpoint import ChartEndpoint


class Props(BaseModel):
    session: Optional[str]
    chart: IChart


class Result(BaseModel):
    chart: IChart


@router.post("/chart/render")
def server_chart_render(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    chart = project.render_chart(props.chart)
    return Result(chart=chart)


# TODO: implement here and use this pattern for other endpoints
class RenderChartEndpoint(ChartEndpoint):
    pass
