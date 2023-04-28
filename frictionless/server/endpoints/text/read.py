from pydantic import BaseModel
from fastapi import Request
from ....resources import TextResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    text: str


@router.post("/text/read")
def server_text_read(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: use detected resource.encoding if indexed
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.path)
    resource = TextResource(path=fullpath)
    text = resource.read_text()

    return Result(text=text)
