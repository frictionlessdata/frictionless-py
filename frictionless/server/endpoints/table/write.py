from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    tablePatch: dict


class Result(BaseModel):
    path: str


@router.post("/table/write")
def server_table_write(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.write_table(props.path, tablePatch=props.tablePatch)
    return Result(path=path)
