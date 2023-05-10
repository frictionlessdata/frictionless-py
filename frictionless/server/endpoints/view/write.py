from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ....resources import FileResource, JsonResource
from ...interfaces import IView
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    view: IView


class Result(BaseModel):
    path: str


@router.post("/view/write")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: rewrite
# TODO: fix not safe
# TODO: remove duplication
def action(project: Project, props: Props) -> Result:
    sa = platform.sqlalchemy
    fs = project.filesystem
    db = project.database

    query = props.view["query"]
    fullpath = fs.get_fullpath(props.path)
    # TODO: use ViewResource?
    resource = JsonResource(data=props.view)
    resource.write_json(path=fullpath)
    resource = FileResource(path=fullpath)
    db.create_record(resource=resource)

    # Get table name
    found = False
    table_names = []
    table_name = resource.name
    template = f"{table_name}%s"
    items = db.list_records()
    for item in items:
        name = item.get("tableName")
        if not name:
            continue
        table_names.append(name)
        if item["path"] == resource.path:
            table_name = name
            found = True
    if not found:
        suffix = 1
        while table_name in table_names:
            table_name = template % suffix
            suffix += 1

    # Create view
    with db.engine.begin() as conn:
        conn.execute(sa.text(f'DROP VIEW IF EXISTS "{table_name}"'))
        conn.execute(sa.text(f'CREATE VIEW "{table_name}" AS {query}'))
        conn.execute(
            sa.update(db.records)
            .where(db.records.c.path == props.path)
            .values(tableName=table_name)
        )

    return Result(path=props.path)
