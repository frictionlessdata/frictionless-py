from __future__ import annotations
from typing import TYPE_CHECKING, List
from ...resources import TableResource
from ...schema import Schema
from .. import types

if TYPE_CHECKING:
    from ..project import Project


def write_table(
    project: Project,
    *,
    path: str,
    rows: List[types.IRow],
    schema: types.IDescriptor,
):
    fs = project.filesystem

    # Write
    fullpath = fs.get_fullpath(path)
    resource = TableResource(data=rows, schema=Schema.from_descriptor(schema))
    resource.write_table(path=str(fullpath))
    path = fs.get_path(fullpath)

    return path
