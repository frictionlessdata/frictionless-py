from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


class ProjectCreateDirectoryProps(BaseModel):
    session: Optional[str]
    directoryname: str


@router.post("/project/create-directory")
def server_project_create_directory(request: Request, props: ProjectCreateDirectoryProps):
    project = request.app.get_project(props.session)
    newdirectory = project.create_directory(props.directoryname)
    return {"path": newdirectory}
