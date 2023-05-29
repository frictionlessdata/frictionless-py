from __future__ import annotations
import re
import stringcase  # type: ignore
from typing import TYPE_CHECKING, List
from slugify.slugify import slugify

if TYPE_CHECKING:
    from ...resource import Resource
    from ..project import Project


def make_record_name(project: Project, *, resource: Resource) -> str:
    md = project.metadata

    # Slugify
    name = slugify(resource.name)
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    name = stringcase.camelcase(name)  # type: ignore

    # Make unique
    names: List[str] = []
    found = False
    template = f"{name}%s"
    for item in md.iter_documents(type="record"):
        item_name: str = item["name"]
        names.append(item_name)
        if item["path"] == resource.path:
            name = item_name
            found = True
    if not found:
        suffix = 1
        while name in names:
            name = template % suffix
            suffix += 1

    return name  # type: ignore
