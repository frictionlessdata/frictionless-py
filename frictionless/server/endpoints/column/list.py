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
                        tableName=descriptor["id"],
                        tablePath=descriptor["path"],
                    )
                )

    return result
