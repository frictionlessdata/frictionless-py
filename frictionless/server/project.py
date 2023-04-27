from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, List, Union
from ..resources import FileResource
from ..resource import Resource
from .database import Database
from .filesystem import Filesystem
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
        database = private / "project.db"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.public = public
        self.private = private
        self.database = Database(f"sqlite:///{database}")
        self.filesystem = Filesystem(str(self.public))

    # File

    def copy_file(
        self, path: str, *, folder: Optional[str] = None, new_path: Optional[str] = None
    ) -> str:
        return self.filesystem.copy_file(path, folder=folder, new_path=new_path)

    def count_files(self):
        return len(self.filesystem.list_files())

    # TODO: review
    def create_file(self, path: str, *, folder: Optional[str] = None) -> str:
        resource = FileResource(path=path)
        name = str(path.split("/")[-1])
        if "?" in name:
            name = str(name.split("?")[0])
        if "." not in name:
            name = f"{name}.csv"
        return self.filesystem.create_file(
            name, bytes=resource.read_bytes(), folder=folder
        )

    def delete_file(self, path: str) -> str:
        self.database.delete_record(path)
        self.filesystem.delete_file(path)
        return path

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

    # Table

    def count_table(self, path: str, *, valid: Optional[bool] = None) -> int:
        return self.database.count_table(path, valid=valid)

    # TODO: review
    def export_table(self, source: str, *, target: str) -> str:
        assert self.filesystem.is_filename(target)
        target = self.filesystem.get_secure_fullpath(target)
        source = self.filesystem.get_secure_fullpath(source)
        self.database.export_table(source, target=target)
        return target

    def query_table(self, query: str) -> ITable:
        return self.database.query_table(query)

    def read_table(
        self,
        path: str,
        *,
        valid: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        desc: Optional[bool] = None,
    ) -> ITable:
        return self.database.read_table(
            path, valid=valid, limit=limit, offset=offset, order=order, desc=desc
        )

    # TODO: review
    def write_table(self, path: str, tablePatch: dict[str, str]) -> str:
        assert self.filesystem.is_filename(path)
        self.database.write_table(
            path, tablePatch=tablePatch, basepath=str(self.filesystem.basepath)
        )
        return path

    # Filesystem

    def get_secure_fullpath(
        self, *paths: Optional[str], deduplicate: Optional[Union[bool, str]] = None
    ) -> str:
        # We need to use resolve here to get normalized path
        fullpath = str(self.public.joinpath(*filter(None, paths)).resolve())
        assert self.get_secure_relpath(fullpath)
        if deduplicate:
            suffix = deduplicate if isinstance(deduplicate, str) else ""
            fullpath = self.deduplicate_fullpath(fullpath, suffix=suffix)
        return fullpath

    def get_secure_relpath(self, fullpath: str) -> str:
        # We need to use resolve here to prevent path traversing
        path = str(Path(fullpath).resolve().relative_to(self.public))
        assert path != "."
        assert path != ""
        return path

    def deduplicate_fullpath(self, fullpath: str, *, suffix: str = "") -> str:
        if os.path.exists(fullpath):
            number = 1
            parts = os.path.splitext(fullpath)
            template = f"{parts[0]} ({suffix}%s){parts[1]}"
            while os.path.exists(fullpath):
                fullpath = template % number
                number += 1
        return fullpath

    def get_filetype(self, path: str) -> Optional[str]:
        resource = Resource(path=path)
        return resource.datatype

    def get_filename(self, path: str) -> str:
        return os.path.basename(path)

    def get_folder(self, path: str) -> str:
        return os.path.dirname(path)

    def is_hidden_path(self, path: str) -> bool:
        for part in os.path.split(path):
            if part.startswith(".") and len(part) > 1:
                return True
        return False

    def is_basepath(self, path: str) -> bool:
        return self.public.samefile(path)

    def is_existent(self, fullpath: str) -> bool:
        return os.path.exists(fullpath)

    def is_filename(self, name: str) -> bool:
        return not os.path.dirname(name)

    def is_folder(self, fullpath: str) -> bool:
        return os.path.isdir(fullpath)

    def is_file(self, fullpath: str) -> bool:
        return os.path.isfile(fullpath)
