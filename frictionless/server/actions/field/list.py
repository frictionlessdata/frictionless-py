import json
from typing import List
from pydantic import BaseModel
from fastapi import Request
from ....schema import Schema
from ....platform import platform
from ...project import Project, IFieldItem
from ...router import router


class Props(BaseModel):
    pass


class Result(BaseModel):
    items: List[IFieldItem]


@router.post("/field/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    sa = platform.sqlalchemy
    db = project.database
    items: List[IFieldItem] = []
    with db.engine.begin() as conn:
        result = conn.execute(
            sa.select(
                db.records.c.path,
                db.records.c.tableName,
                sa.literal_column("json_extract(resource, '$.schema')").label("schema"),
            )
            .where(db.records.c.type == "table")
            .order_by(db.records.c.tableName)
        )
        for row in result:
            schema = Schema.from_descriptor(json.loads(row.schema))
            for field in schema.fields:
                items.append(
                    IFieldItem(
                        # TODO: review why field.name is not required
                        name=field.name,  # type: ignore
                        type=field.type,
                        tableName=row.tableName,
                        tablePath=row.path,
                    )
                )
    return Result(items=items)
