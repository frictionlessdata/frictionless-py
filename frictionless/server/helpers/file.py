from __future__ import annotations
from typing import TYPE_CHECKING
from ...resources import FileResource

if TYPE_CHECKING:
    from ..project import Project


def test_file(project: Project, *, path: str):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    return fullpath.exists()


def read_file(project: Project, *, path: str):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    resource = FileResource(path=str(fullpath))
    bytes = resource.read_file()

    return bytes


def write_file(project: Project, *, path: str, bytes: bytes):
    fs = project.filesystem

    fullpath = fs.get_fullpath(path)
    source = FileResource(data=bytes)
    target = FileResource(path=str(fullpath))
    source.write_file(target)
    path = fs.get_path(fullpath)

    return path
