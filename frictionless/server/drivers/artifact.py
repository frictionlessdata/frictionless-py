from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..project import Project


class Artifact:
    reports: Path

    def __init__(self, project: Project):
        # Ensure reports folder
        self.reports = project.private / "reports"
        if not self.reports.is_dir():
            self.reports.mkdir()
