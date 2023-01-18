from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..router import router


class ProjectCreateRecordProps(BaseModel):
    session: Optional[str]
    path: str


@router.post("/project/create-record")
def server_project_create_record(request: Request, props: ProjectCreateRecordProps):
    project = request.app.get_project(props.session)
    record = project.create_record(props.path)
    return {"record": record.to_descriptor()}
