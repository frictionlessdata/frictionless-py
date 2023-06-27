from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from pydantic import BaseModel

from ... import helpers
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    data: Any
    deduplicate: Optional[bool] = None


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/json/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = helpers.write_json(
        project, path=props.path, data=props.data, deduplicate=props.deduplicate
    )
    return Result(path=path)
