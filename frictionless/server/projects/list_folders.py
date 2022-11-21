from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectListFoldersProps(BaseModel):
    session: Optional[str]


@router.post("/project/list-folders")
def server_project_list_folders(request: Request, props: ProjectListFoldersProps):
    config = request.app.config
    project = Project(config, session=props.session)
    directories = project.list_folders()
    return {"directories": directories}
