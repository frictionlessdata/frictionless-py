from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    with_folders: bool
    only_folders: bool


class Result(BaseModel):
    paths: List[str]


@router.post("/file/list")
def server_file_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    paths = project.file_list(
        with_folders=props.with_folders,
        only_folders=props.only_folders,
    )
    return Result(paths=paths)
