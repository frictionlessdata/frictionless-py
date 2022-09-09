from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectListFilesProps(BaseModel):
    session: Optional[str]


@router.post("/project/list-files")
def server_file_create(request: Request, props: ProjectListFilesProps):
    config = request.app.config
    project = Project(config, session=props.session)
    paths = project.list_files()
    return {"paths": paths}
