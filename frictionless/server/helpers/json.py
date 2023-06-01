from __future__ import annotations
from typing import TYPE_CHECKING, Any
from ...resources import JsonResource

if TYPE_CHECKING:
    from ..project import Project


def read_json(project: Project, *, path: str):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    resource = JsonResource(path=str(fullpath))
    data = resource.read_json()

    return data


def write_json(project: Project, *, path: str, data: Any):
    fs = project.filesystem

    # Write
    fullpath = fs.get_fullpath(path)
    resource = JsonResource(data=data)
    resource.write_json(path=str(fullpath))
    path = fs.get_path(fullpath)

    return path
