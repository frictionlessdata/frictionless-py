from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectUpdateRecordProps(BaseModel):
    session: Optional[str]
    resource: dict


@router.post("/project/create-record")
def server_project_update_record(request: Request, props: ProjectUpdateRecordProps):
    config = request.app.config
    project = Project(config, session=props.session)
    raise NotImplementedError(project)
