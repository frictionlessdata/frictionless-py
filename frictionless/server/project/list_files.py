from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


class ProjectListFilesProps(BaseModel):
    session: Optional[str]


@router.post("/project/list-files")
def server_project_list_files(request: Request, props: ProjectListFilesProps):
    project = request.app.get_project(props.session)
    paths = project.list_files()
    return {"paths": paths}
