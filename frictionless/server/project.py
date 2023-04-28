from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, List, Union
from ..resources import FileResource
from ..resource import Resource
from .filesystem import Filesystem
from .metadata import Metadata
from .database import Database
from .interfaces import ITable, IFile, IFileItem


# TODO: move specific logic to endpoint classes
class Project:
    public: Path
    private: Path
    database: Database
    filesystem: Filesystem

    def __init__(self, folder: Optional[str] = None):
        # Ensure structure
        public = Path(folder or "")
        private = public / ".frictionless"
        metadata = private / "datapackage.json"
        # TODO: rename to datapackage.db
        database = private / "project.db"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.public = public
        self.private = private
        self.filesystem = Filesystem(str(self.public))
        self.metadata = Metadata(str(metadata))
        self.database = Database(f"sqlite:///{database}")

    # File

    # TODO: fix not safe (move resource creation to filesystem)
    def index_file(self, path: str) -> Optional[IFile]:
        file = self.select_file(path)
        if file:
            if not file.get("record"):
                resource = Resource(path=path, basepath=str(self.public))
                record = self.database.create_record(resource)
                file["type"] = record["type"]
                file["record"] = record
            return file

    def list_files(self) -> List[IFileItem]:
        records = self.database.list_records()
        mapping = {record["path"]: record for record in records}
        items = self.filesystem.list_files()
        for item in items:
            record = mapping.get(item["path"])
            if record and "errorCount" in record:
                item["errorCount"] = record["errorCount"]
        return items

    def move_file(self, path: str, *, folder: Optional[str] = None) -> str:
        source = path
        target = self.filesystem.move_file(path, folder=folder)
        self.database.move_record(source, target)
        return target

    def read_file(self, path: str) -> bytes:
        return self.filesystem.read_file(path)

    def rename_file(self, path: str, *, name: str) -> str:
        source = path
        target = self.filesystem.rename_file(path, name=name)
        self.database.move_record(source, target)
        return target

    def select_file(self, path: str) -> Optional[IFile]:
        item = self.filesystem.select_file(path)
        if item:
            # TODO: don't use interfaces runtime here and in other places!
            # [correct] file: IFile = dict(**item)
            file = IFile(**item)
            record = self.database.select_record(path)
            if record:
                file["type"] = record["type"]
                file["record"] = record
            return file

    def update_file(self, path: str, *, resource: dict, reindex: Optional[bool] = None):
        if reindex:
            res = Resource.from_descriptor(resource, basepath=str(self.public))
            self.database.delete_record(path)
            self.database.create_record(res)
            return
        return self.database.update_record(path, resource=resource)

    def upload_file(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        return self.filesystem.create_file(name, bytes=bytes, folder=folder)

    # TODO: it should trigger re-indexing etc
    def write_file(self, path: str, *, bytes: bytes) -> None:
        return self.filesystem.write_file(path, bytes=bytes)
