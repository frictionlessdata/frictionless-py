from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


class ProjectUpdateRecordProps(BaseModel):
    session: Optional[str]
    resource: dict


@router.post("/project/create-record")
def server_project_update_record(request: Request, props: ProjectUpdateRecordProps):
    project = request.app.get_project(props.session)
    raise NotImplementedError(project)
