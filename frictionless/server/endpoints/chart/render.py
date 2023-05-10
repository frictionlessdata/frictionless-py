from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ...interfaces import IChart
from ...project import Project
from ...router import router


class Props(BaseModel):
    chart: IChart


class Result(BaseModel):
    chart: IChart


@router.post("/chart/render")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: review/rewrite
def action(project: Project, props: Props) -> Result:
    db = project.database

    chart = props.chart.copy()
    path = chart.get("data", {}).pop("url", None)
    if not path:
        return Result(chart=chart)
    record = db.select_record(path)
    if not record:
        return Result(chart=chart)
    table_name = record.get("tableName")
    if not table_name:
        return Result(chart=chart)
    # TODO: cherry-pick fields based on presense in the chart
    result = db.query(f'SELECT * from "{table_name}"')
    # TODO: check if some data types need to be stringified
    chart["data"]["values"] = result["rows"]

    return Result(chart=chart)
