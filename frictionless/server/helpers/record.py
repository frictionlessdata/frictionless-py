from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional, cast

import stringcase  # type: ignore
from slugify.slugify import slugify
from tinydb import Query

from ...exception import FrictionlessException
from ...resource import Resource
from .. import models, types

if TYPE_CHECKING:
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

    # Update record
    updated = False
    record = read_record_or_raise(project, path=path)
    if toPath:
        updated = True
        record.name = name_record(project, path=toPath)
        record.path = toPath
        record.resource["path"] = toPath
    if toType:
        updated = True
        record.type = toType
    if resource:
        updated = True
        record.resource = resource

    # Write record
    if updated:
        md.write_document(name=record.name, type="record", descriptor=record.dict())

    # Clear database
    # TODO: use smarter logic to delete only if needed
    if updated and not toPath:
        delete_record(project, path=path, onlyFromDatabase=True)

    return record


def delete_record(project: Project, *, path: str, onlyFromDatabase: bool = False):
    md = project.metadata
    db = project.database

    # Read record
    record = read_record(project, path=path)
    if not record:
        return None

    # Delete from database
    db.delete_artifact(name=record.name, type="report")
    db.delete_artifact(name=record.name, type="measure")
    db.delete_table(name=record.name)

    # Delete from metadata
    if not onlyFromDatabase:
        md.delete_document(name=record.name, type="record")


def read_record_or_raise(project: Project, *, path: str):
    record = read_record(project, path=path)
    if not record:
        raise FrictionlessException("record not found")
    return record


def read_record(project: Project, *, path: str):
    md = project.metadata

    descriptor = md.find_document(type="record", query=Query().path == path)
    if not descriptor:
        return None
    return models.Record.parse_obj(descriptor)


def name_record(project: Project, *, path: str) -> str:
    md = project.metadata

    # Make slugified
    name = Resource(path=path).name
    name = slugify(name)
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    name = cast(str, stringcase.camelcase(name))  # type: ignore
    name = name.replace("_", "")  # if something not replaced by camelcase

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
