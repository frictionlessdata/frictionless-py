from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router
from .. import json


class Props(BaseModel):
    path: Optional[str]
    # TODO: Use IPackage
    package: Optional[dict]
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


@router.post("/package/create")
def server_package_create(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = props.path or "datapackage.json"
    data = props.package or {"resources": []}
    result = json.write.action(
        project, json.write.Props(path=path, data=data, deduplicate=True)
    )
    return Result(path=result.path)
