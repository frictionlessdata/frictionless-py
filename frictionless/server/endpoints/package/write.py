from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from .. import json


class Props(BaseModel):
    path: str
    data: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/package/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    db = project.database

    db.delete_record(props.path)
    result = json.write.action(
        project, json.write.Props(path=props.path, data=props.data)
    )

    return Result(path=result.path)
