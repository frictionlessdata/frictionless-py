from __future__ import annotations
from typing import List, TYPE_CHECKING
from tinydb import Query
from pydantic import BaseModel
from fastapi import Request
from ....platform import platform
from ....exception import FrictionlessException
from ....resources import TableResource
from ....resource import Resource
from ...project import Project
from ...router import router
from ...interfaces import IDescriptor
from ...interfaces import IDescriptor
from ... import settings
from ... import helpers

if TYPE_CHECKING:
    from ....report import Report
    from ....table import Row


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    resource: IDescriptor


@router.post("/resource/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: raise if already exist?
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    md = project.metadata

    # Check existence
    if md.resources.get(Query().path == props.path):
        raise FrictionlessException("Resource already exists")

    # Index resource
    path, basepath = fs.get_path_and_basepath(props.path)
    resource = Resource(path=path, basepath=basepath)
    id = make_unique_id(project, resource)
    report = index_resource(project, resource, id)
    print(report)

    # Extend resource
    resource.custom["id"] = id
    resource.custom["datatype"] = resource.datatype

    # Write resource
    descriptor = resource.to_descriptor()
    md.resources.insert(md.document(id, **descriptor))  # type: ignore
    return Result(resource=descriptor)


# Internal


def index_resource(project: Project, resource: Resource, id: str) -> Report:
    db = project.database
    sa = platform.sqlalchemy

    # Non-tabular
    if not isinstance(resource, TableResource):
        return resource.validate()

    # Tabular
    with resource, db.engine.begin() as conn:
        # Remove existing table
        existing_table = db.metadata.tables.get(id)
        if existing_table is not None:
            db.metadata.drop_all(conn, tables=[existing_table])

        # Create new table
        table = db.mapper.write_schema(
            resource.schema,
            table_name=id,
            with_metadata=True,
        )
        table.to_metadata(db.metadata)
        db.metadata.create_all(conn, tables=[table])

        # Write row
        def on_row(row: Row):
            buffer.append(db.mapper.write_row(row, with_metadata=True))
            if len(buffer) > settings.BUFFER_SIZE:
                conn.execute(sa.insert(table), buffer)
                buffer.clear()

        # Validate/iterate
        buffer: List[Row] = []
        report = resource.validate(on_row=on_row)
        if len(buffer):
            conn.execute(sa.insert(table), buffer)

        return report


def make_unique_id(project: Project, resource: Resource) -> str:
    md = project.metadata

    ids: List[str] = []
    found = False
    id = helpers.make_id(resource.name)
    template = f"{id}%s"
    for item in md.resources:
        item_id: str = item["id"]
        ids.append(item_id)
        if item["path"] == resource.path:
            id = item_id
            found = True
    if not found:
        suffix = 1
        while id in ids:
            id = template % suffix
            suffix += 1

    return id
