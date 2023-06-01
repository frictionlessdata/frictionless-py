from __future__ import annotations
import re
import stringcase  # type: ignore
from tinydb import Query
from typing import TYPE_CHECKING, List, Optional
from slugify.slugify import slugify
from ...exception import FrictionlessException
from .. import models
from .. import types

if TYPE_CHECKING:
    from ...resource import Resource
    from ..project import Project


# TODO: update all the project's packages/resources as well
def patch_record(
    project: Project,
    *,
    path: str,
    toPath: Optional[str] = None,
    toType: Optional[str] = None,
    resource: Optional[types.IDescriptor] = None,
    isDataChanged: bool = False,
):
    md = project.metadata
    db = project.database

    # Update record
    record = read_record_or_raise(project, path=path)
    if toPath:
        record.name = name_record(project, path=toPath)
        record.path = toPath
        record.resource["path"] = toPath
    if toType:
        record.type = toType
    if resource:
        record.resource = resource
    md.write_document(name=record.name, type="record", descriptor=record.dict())

    # Clear database
    # TODO: use smarter logic to clear only if needed
    if not toPath:
        db.delete_table(name=record.name)
        db.delete_artifact(name=record.name, type="report")
        db.delete_artifact(name=record.name, type="measure")

    return record


def read_record_or_raise(project: Project, *, path: str):
    record = read_record(project, path=path)
    if not record:
        raise FrictionlessException("record not found")
    return record


def read_record(project: Project, *, path: str):
    md = project.metadata

    descriptor = md.find_document(type="record", query=Query().path == path)
    if descriptor:
        return models.Record.parse_obj(descriptor)


def name_record(project: Project, *, path: str) -> str:
    md = project.metadata

    # Make slugified
    name = Resource(path=path).name
    name = slugify(name)
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    name = stringcase.camelcase(name)  # type: ignore

    # Make unique
    names: List[str] = []
    found = False
    template = f"{name}%s"
    for item in md.iter_documents(type="record"):
        item_name: str = item["name"]
        names.append(item_name)
        if item["path"] == path:
            name = item_name
            found = True
    if not found:
        suffix = 1
        while name in names:
            name = template % suffix
            suffix += 1

    return name  # type: ignore
