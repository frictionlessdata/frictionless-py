from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    tablePatch: dict


class Result(BaseModel):
    path: str


@router.post("/table/save")
def server_table_save(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.save_table(props.path, tablePatch=props.tablePatch)
    return Result(path=path)
