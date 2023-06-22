from __future__ import annotations

from copy import deepcopy

from fastapi import Request
from pydantic import BaseModel

from ....platform import platform
from ... import types
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    chart: types.IChart


class Result(BaseModel, extra="forbid"):
    chart: types.IChart


@router.post("/chart/render")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    from ... import endpoints

    db = project.database
    sa = platform.sqlalchemy
    chart = deepcopy(props.chart)

    # Return if no path
    path = chart.get("data", {}).pop("url", None)
    if not path:
        return Result(chart=chart)

    # Ensure record
    record = endpoints.file.index.action(
        project, endpoints.file.index.Props(path=path)
    ).record

    # TODO: cherry-pick fields based on presense in the chart
    # TODO: check if some data types need to be stringified
    with db.engine.begin() as conn:
        table = db.get_table(name=record.name)
        result = conn.execute(sa.select(table))
        values = list(dict(item) for item in result.mappings())
        chart["data"]["values"] = values

    return Result(chart=chart)
