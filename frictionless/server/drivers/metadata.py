from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from typing import TYPE_CHECKING
from ...resources import JsonResource

if TYPE_CHECKING:
    from ..project import Project


class Metadata:
    fullpath: Path

    def __init__(self, project: Project):
        self.fullpath = project.private / "metadata.json"

        # Ensure metadata file
        if not self.fullpath.exists():
            JsonResource(data={}).write_json(path=self.fullpath)

    def read(self) -> Dict[str, Dict[str, Any]]:
        resource = JsonResource(path=str(self.fullpath))
        return resource.read_json()

    def write(self, metadata: Dict[str, Dict[str, Any]]):
        resource = JsonResource(data=metadata)
        resource.write_json(path=str(self.fullpath))
