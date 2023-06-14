from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import types


# TODO: update view itself


class Props(BaseModel):
    path: str
    data: Optional[Any]
    toPath: Optional[str]
    resource: Optional[types.IDescriptor]


class Result(BaseModel):
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
