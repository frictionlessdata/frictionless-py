from __future__ import annotations

from typing import TYPE_CHECKING

from tinydb import Query

from .. import models

if TYPE_CHECKING:
    from ..project import Project


def read_measure(project: Project, *, path: str):
    md = project.metadata

    descriptor = md.find_document(type="measure", query=Query().path == path)
    if descriptor:
        return models.Measure.parse_obj(descriptor)
