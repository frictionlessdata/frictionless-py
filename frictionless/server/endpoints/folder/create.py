from pydantic import BaseModel
from fastapi import Request
from ....exception import FrictionlessException
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    path: str


@router.post("/folder/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Create
    target = fs.get_fullpath(props.path)
    if target.exists():
        raise FrictionlessException("Folder already exists")
    target.mkdir(parents=True)
    path = fs.get_path(target)

    return Result(path=path)
