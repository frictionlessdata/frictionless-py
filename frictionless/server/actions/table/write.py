from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    tablePatch: dict


class Result(BaseModel):
    path: str


@router.post("/table/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: rework
def action(project: Project, props: Props) -> Result:
    assert project.is_filename(props.path)
    project.database.write_table(
        props.path, tablePatch=props.tablePatch, basepath=str(project.public)
    )
    return Result(path=props.path)
