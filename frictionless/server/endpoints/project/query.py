from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IQueryData
from ...router import router


class Props(BaseModel):
    query: str


class Result(BaseModel):
    data: IQueryData


@router.post("/project/query")
def server_project_query(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    data = project.query_project(props.query)
    return Result(data=data)
