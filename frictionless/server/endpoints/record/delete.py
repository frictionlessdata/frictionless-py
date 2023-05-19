from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    id: str


class Result(BaseModel, extra="forbid"):
    id: str


@router.post("/record/delete")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    ids = md.delete_document(id=props.id, type="record")
    if not ids:
        raise FrictionlessException("record does not exist")

    return Result(id=props.id)
