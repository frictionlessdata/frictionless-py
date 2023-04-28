from pydantic import BaseModel
from fastapi import Request
from ....resources import TextResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    text: str


class Result(BaseModel):
    path: str


@router.post("/text/write")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_secure_fullpath(props.path)
    resource = TextResource(data=props.text)
    resource.write_text(path=fullpath)

    return Result(path=props.path)
