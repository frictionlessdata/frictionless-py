from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ...exception import FrictionlessException
from ...resources import TextResource

if TYPE_CHECKING:
    from ..project import Project


def read_text(project: Project, *, path: str, size: Optional[int] = None):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    resource = TextResource(path=str(fullpath))
    text = resource.read_text(size=size)

    return text


def write_text(
    project: Project,
    *,
    path: str,
    text: str,
    overwrite: Optional[bool] = None,
    deduplicate: Optional[bool] = None,
):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path, deduplicate=deduplicate)
    if not overwrite and fullpath.exists():
        raise FrictionlessException("text already exists")
    source = TextResource(data=text)
    target = TextResource(path=str(fullpath))
    source.write_text(target)
    path = fs.get_path(fullpath)

    return path
