from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    pass


class Result(BaseModel):
    count: int


@router.post("/file/count")
def server_file_count(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    count = project.count_files()
    return Result(count=count)
