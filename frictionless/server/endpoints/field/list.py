from __future__ import annotations
from typing import List
from pydantic import BaseModel
from fastapi import Request
from ....schema import Schema
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel):
    pass


class Result(BaseModel):
    items: List[models.FieldItem]


@router.post("/field/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    md = project.metadata

    result = Result(items=[])
    for resource in md.iter_documents(type="resource"):
        schema = Schema.from_descriptor(resource["schema"])
        for field in schema.fields:
            result.items.append(
                models.FieldItem(
                    name=field.name,
                    type=field.type,
                    tableName=resource["id"],
                    tablePath=resource["path"],
                )
            )

    return result
