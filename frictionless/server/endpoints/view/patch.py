from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from pydantic import BaseModel

from ... import types
from ...project import Project
from ...router import router

# TODO: update view itself


class Props(BaseModel, extra="forbid"):
    path: str
    data: Optional[Any]
    toPath: Optional[str]
    resource: Optional[types.IDescriptor]


class Result(BaseModel, extra="forbid"):
    path: str


@router.post("/view/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    from ... import endpoints

    # Base patch
    result = endpoints.json.patch.action(
        project,
        endpoints.json.patch.Props(
            path=props.path,
            data=props.data,
            toPath=props.toPath,
        ),
    )

    # Update database
    # TODO: update view in the database

    return Result(path=result.path)
