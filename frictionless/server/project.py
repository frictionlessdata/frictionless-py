from __future__ import annotations
from pathlib import Path
from typing import Optional
from .stores import Filesystem, Metadata, Database


class Project:
    public: Path
    private: Path
    filesystem: Filesystem
    metadata: Metadata
    database: Database

    def __init__(self, basepath: Optional[str] = None):
        # Ensure structure
        self.public = Path(basepath or "")
        self.private = self.public / ".frictionless"
        self.public.mkdir(parents=True, exist_ok=True)
        self.private.mkdir(parents=True, exist_ok=True)

        # Create drivers
        self.filesystem = Filesystem(self)
        self.metadata = Metadata(self)
        self.database = Database(self)
