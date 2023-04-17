from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    count: int


@router.post("/table/count")
def server_table_count(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    count = project.count_table(props.path)
    return Result(count=count)
