from __future__ import annotations

from typing import List

from fastapi import Request
from pydantic import BaseModel

from ....schema import Schema
from ... import models
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    pass


class Result(BaseModel, extra="forbid"):
    columns: List[models.Column]


@router.post("/column/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    result = Result(columns=[])
    for descriptor in md.iter_documents(type="record"):
        if "schema" in descriptor["resource"]:
            schema = Schema.from_descriptor(descriptor["resource"]["schema"])
            for field in schema.fields:
                result.columns.append(
                    models.Column(
                        name=field.name,
                        type=field.type,
                        tableName=descriptor["name"],
                        tablePath=descriptor["path"],
                    )
                )

    return result
