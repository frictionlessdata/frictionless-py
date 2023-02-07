from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFileItem
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    items: List[IFileItem]


@router.post("/file/list")
def server_file_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    items = project.list_files()
    return Result(items=items)
