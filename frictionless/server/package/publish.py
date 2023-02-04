import json
from typing import Optional, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class props(BaseModel):
    session: Optional[str]
    params: dict


# TODO: provide proper types
class Result(BaseModel):
    content: Any


@router.post("/package/publish")
def server_package_publish(request: Request, props: props) -> Result:
    project: Project = request.app.get_project(props.session)
    json_data = json.dumps(project.publish_package(**props.params))
    return Result(content=json_data)
