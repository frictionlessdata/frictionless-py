from __future__ import annotations
from typing import TYPE_CHECKING
from ...package import Package

if TYPE_CHECKING:
    from ..project import Project


class Metadata:
    package: Package

    def __init__(self, project: Project):
        # Ensure metadata file
        fullpath = project.private / "metadata.json"
        if not fullpath.exists():
            Package(resources=[]).to_json(str(fullpath))

        # Open data package
        self.package = Package.from_descriptor(str(fullpath), allow_invalid=True)
