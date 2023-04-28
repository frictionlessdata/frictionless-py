from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from . import list


class Props(BaseModel):
    pass


class Result(BaseModel):
    count: int


@router.post("/file/count")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    result = list.action(project, list.Props())
    count = len(result.items)

    return Result(count=count)
