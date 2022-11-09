from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class SessionsDeleteFileProps(BaseModel):
    session: Optional[str]
    path: str


@router.post("/project/delete-file")
def server_project_delete_file(request: Request, props: SessionsDeleteFileProps):
    config = request.app.config
    project = Project(config, session=props.session)
    path = project.delete_file(props.path)
    return {"path": path}
