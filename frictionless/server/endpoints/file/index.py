from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFile
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    file: Optional[IFile]


@router.post("/file/index")
def server_file_index(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    file = project.index_file(props.path)
    return Result(file=file)
