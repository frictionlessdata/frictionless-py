from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..project import Project
from ..router import router


class ProjectReadFileProps(BaseModel):
    session: Optional[str]
    path: str


@router.post("/project/read-file")
def server_resource_extract_text(request: Request, props: ProjectReadFileProps):
    config = request.app.config
    project = Project(config, session=props.session)
    # TODO: handle errors
    text = project.read_file(props.path)
    return dict(text=text)
