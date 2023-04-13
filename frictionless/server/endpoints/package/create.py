from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    pass


class Result(BaseModel):
    path: str


@router.post("/package/create")
def server_package_create(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    path = project.create_package()
    return Result(path=path)
