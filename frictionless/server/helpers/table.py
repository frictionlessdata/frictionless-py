from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ...exception import FrictionlessException
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
    overwrite: Optional[bool] = None,
    deduplicate: Optional[bool] = None,
):
    fs = project.filesystem

    # Write
    fullpath = fs.get_fullpath(path, deduplicate=deduplicate)
    if not overwrite and fullpath.exists():
        raise FrictionlessException("table already exists")
    resource = TableResource(data=rows, schema=Schema.from_descriptor(schema))
    resource.write_table(path=str(fullpath))
    path = fs.get_path(fullpath)

    return path
