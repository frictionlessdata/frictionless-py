from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    # TODO: render provided test (not by path)
    path: str


class Result(BaseModel):
    text: str


@router.post("/text/render")
def server_text_render(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    text = project.render_text(props.path)
    return Result(text=text)
