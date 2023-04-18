from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    text: str


@router.post("/text/read")
def server_text_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    text = project.read_text(props.path)
    return Result(text=text)
