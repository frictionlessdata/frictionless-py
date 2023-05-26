from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    record: models.Record


@router.post("/record/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:  # type: ignore
    pass
