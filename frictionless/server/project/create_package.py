from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectCreatePackageProps(BaseModel):
    session: Optional[str]


@router.post("/project/create-package")
def server_project_create_package(request: Request, props: ProjectCreatePackageProps):
    config = request.app.config
    project = Project(config, session=props.session)
    path = project.create_package()
    return {"path": path}
