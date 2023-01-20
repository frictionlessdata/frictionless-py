from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


class ProjectCopyFileProps(BaseModel):
    session: Optional[str]
    filename: str
    destination: str


@router.post("/project/copy-file")
def server_project_copy_file(request: Request, props: ProjectCopyFileProps):
    project = request.app.get_project(props.session)
    filepath = project.copy_file(props.filename, props.destination)
    return {"path": filepath}
