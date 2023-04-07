from __future__ import annotations
import secrets
import datetime
from pathlib import Path
from typing import Optional, List, Any, Dict
from ..resources import FileResource
from ..exception import FrictionlessException
from ..package import Package
from ..resource import Resource
from .database import Database
from .filesystem import Filesystem
from .interfaces import IQueryData, ITable, IFile, IFileItem, IFieldItem
from .. import settings
from .. import portals


class Project:
    is_root: bool
    session: Optional[str]
    public: Path
    private: Path
    database: Database
    filesystem: Filesystem

    def __init__(
        self,
        *,
        basepath: Optional[str] = None,
        session: Optional[str] = None,
        is_root: bool = False,
    ):
        # Provide authz
        base = Path(basepath or "")
        if is_root:
            assert not session
        if not is_root:
            if not session:
                session = secrets.token_urlsafe(16)
            assert len(session) == 22

        # Ensure structure
        public = base / (session or "")
        private = public / ".frictionless"
        database = private / "project.db"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.is_root = is_root
        self.session = session
        self.public = public
        self.private = private
        self.database = Database(f"sqlite:///{database}")
        self.filesystem = Filesystem(str(self.public))

    # File

    def copy_file(self, path: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.copy_file(path, folder=folder)

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
                file["record"] = self.database.create_record(resource)
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
            file = IFile(**item)
            record = self.database.select_record(path)
            if record:
                file["record"] = record
            return file

    # TODO: it should trigger re-indexing etc
    def update_file(self, path: str, *, resource: dict):
        return self.database.update_record(path, resource=resource)

    def upload_file(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        return self.filesystem.create_file(name, bytes=bytes, folder=folder)

    # TODO: it should trigger re-indexing etc
    def write_file(self, path: str, *, bytes: bytes) -> None:
        return self.filesystem.write_file(path, bytes=bytes)

    # Field

    def list_fields(self) -> List[IFieldItem]:
        return self.database.list_fields()

    # Folder

    def create_folder(self, name: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.create_folder(name, folder=folder)

    # Json

    def read_json(self, path: str) -> Any:
        return self.filesystem.read_json(path)

    def write_json(self, path: str, *, data: Any):
        return self.filesystem.write_json(path, data=data)

    # Metadata

    def write_metadata(self, path: str, *, data: Dict[str, Any]):
        self.database.delete_record(path)
        return self.filesystem.write_json(path, data=data)

    # Package

    def create_package(self):
        path = settings.PACKAGE_PATH
        self.filesystem.write_json(path, data={"resources": []})
        return path

    def publish_package(self, path: str, *, control: Dict[str, Any]):
        return self.filesystem.publish_package(path, control=control)

    def write_package(self, path: str, *, data: Dict[str, Any]):
        self.database.delete_record(path)
        return self.filesystem.write_json(path, data=data)

    # Project

    def index_project(self):
        pass

    def query_project(self, query: str) -> IQueryData:
        return self.database.query(query)

    # Table

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
    ) -> ITable:
        return self.database.read_table(path, valid=valid, limit=limit, offset=offset)

    # TODO: review
    def write_table(self, path: str, tablePatch: dict[str, str]) -> str:
        assert self.filesystem.is_filename(path)
        self.database.write_table(
            path, tablePatch=tablePatch, basepath=str(self.filesystem.basepath)
        )
        return path

    # Text

    def read_text(self, path: str) -> str:
        return self.filesystem.read_text(path)

    def render_text(self, path: str) -> str:
        return self.filesystem.render_text(path, livemark=self.is_root)

    def write_text(self, path: str, *, text: str):
        return self.filesystem.write_text(path, text=text)
