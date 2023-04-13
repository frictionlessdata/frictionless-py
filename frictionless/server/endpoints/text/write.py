from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    text: str


class Result(BaseModel):
    path: str


@router.post("/text/write")
def server_text_write(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    project.write_text(props.path, text=props.text)
    return Result(path=props.path)
