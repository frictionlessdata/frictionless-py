from __future__ import annotations
from pathlib import Path
from typing import Optional
from .drivers import Filesystem, Metadata, Database, Artifact


class Project:
    public: Path
    private: Path
    artifact: Artifact
    filesystem: Filesystem
    database: Database
    metadata: Metadata

    def __init__(self, basepath: Optional[str] = None):
        # Ensure structure
        self.public = Path(basepath or "")
        self.private = self.public / ".frictionless"
        self.public.mkdir(parents=True, exist_ok=True)
        self.private.mkdir(parents=True, exist_ok=True)

        # Create drivers
        self.artifact = Artifact(self)
        self.filesystem = Filesystem(self)
        self.database = Database(self)
        self.metadata = Metadata(self)
