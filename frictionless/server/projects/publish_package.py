import json
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Request

from ..project import Project
from ..router import router


class ProjectPublishPackageProps(BaseModel):
    session: Optional[str]
    params: dict


@router.post("/project/publish-package")
def server_project_publish_package(request: Request, props: ProjectPublishPackageProps):
    config = request.app.config
    project = Project(config, session=props.session)
    json_data = json.dumps(project.publish_package(**props.params))
    return JSONResponse(content=json_data)
