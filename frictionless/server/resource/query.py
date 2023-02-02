from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IQueryResult
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    query: str


class Result(BaseModel):
    result: IQueryResult


@router.post("/resource/query")
def server_resource_query(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    result = project.resource_query(props.query)
    return Result(result=result)
