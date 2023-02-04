from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IListedFile
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    files: List[IListedFile]


@router.post("/resource/list")
def server_resource_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    files = project.list_resources()
    return Result(files=files)
