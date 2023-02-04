from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IListedRecord
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    records: List[IListedRecord]


@router.post("/resource/list")
def server_resource_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    records = project.list_resources()
    return Result(records=records)
