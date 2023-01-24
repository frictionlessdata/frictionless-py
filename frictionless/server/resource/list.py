from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    records: List


@router.post("/resource/delete")
def server_resource_delete(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    records = project.resource_list()
    return Result(records=records)
