from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IData
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    data: IData


@router.post("/data/read")
def server_data_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    data = project.read_data(props.path)
    return Result(data=data)
