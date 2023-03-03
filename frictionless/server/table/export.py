from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    name: str
    format: str


class Result(BaseModel):
    path: str


@router.post("/table/export")
def server_table_export(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.export_table(props.path, name=props.name, format=props.format)
    return Result(path=path)
