from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectMoveFileProps(BaseModel):
    session: Optional[str]
    filename: str
    destination: str


@router.post("/project/move-file")
def server_project_move_file(request: Request, props: ProjectMoveFileProps):
    config = request.app.config
    project = Project(config, session=props.session)
    filepath = project.move_file(props.filename, props.destination)
    return {"path": filepath}
