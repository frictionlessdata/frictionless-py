from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ...exception import FrictionlessException
from ...resources import JsonResource

if TYPE_CHECKING:
    from ..project import Project


def read_json(project: Project, *, path: str):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    resource = JsonResource(path=str(fullpath))
    data = resource.read_json()

    return data


def write_json(
    project: Project,
    *,
    path: str,
    data: Any,
    overwrite: Optional[bool] = None,
    deduplicate: Optional[bool] = None,
):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path, deduplicate=deduplicate)
    if not overwrite and fullpath.exists():
        raise FrictionlessException("json already exists")
    source = JsonResource(data=data)
    target = JsonResource(path=str(fullpath))
    source.write_json(target)
    path = fs.get_path(fullpath)

    return path
