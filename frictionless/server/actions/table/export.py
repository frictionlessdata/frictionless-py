from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    source: str
    target: str


class Result(BaseModel):
    path: str


@router.post("/table/export")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: rework
def action(project: Project, props: Props) -> Result:
    assert project.is_filename(props.target)
    target = project.get_secure_fullpath(props.target)
    source = project.get_secure_fullpath(props.source)
    project.database.export_table(source, target=target)
    return Result(path=target)
