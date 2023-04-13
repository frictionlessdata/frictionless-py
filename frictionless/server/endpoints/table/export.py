from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    source: str
    target: str


class Result(BaseModel):
    path: str


@router.post("/table/export")
def server_table_export(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.export_table(props.source, target=props.target)
    return Result(path=path)
