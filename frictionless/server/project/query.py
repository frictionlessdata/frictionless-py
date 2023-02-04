from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IQueryData
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    query: str


class Result(BaseModel):
    data: IQueryData


@router.post("/project/query")
def server_project_query(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    data = project.query(props.query)
    return Result(data=data)
