from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    withFolders: bool = False
    onlyFolders: bool = False


class Result(BaseModel):
    paths: List[str]


@router.post("/file/list")
def server_file_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    paths = project.file_list(
        with_folders=props.withFolders,
        only_folders=props.onlyFolders,
    )
    return Result(paths=paths)
