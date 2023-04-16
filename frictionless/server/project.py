from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Any, Dict
from ..platform import platform
from ..resources import FileResource
from ..resource import Resource
from .database import Database
from .filesystem import Filesystem
from .interfaces import IQueryData, ITable, IFile, IFileItem, IFieldItem, IChart, IView


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

    # Chart

    def create_chart(self):
        return self.filesystem.create_chart()

    def render_chart(self, chart: IChart) -> IChart:
        chart = chart.copy()
        path = chart.get("data", {}).pop("url", None)
        if not path:
            return chart
        record = self.database.select_record(path)
        if not record:
            return chart
        table_name = record.get("tableName")
        if not table_name:
            return chart
        # TODO: cherry-pick fields based on presense in the chart
        result = self.database.query(f'SELECT * from "{table_name}"')
        # TODO: check if some data types need to be stringified
        chart["data"]["values"] = result["rows"]
        return chart

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
        return self.filesystem.create_package()

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

    def render_text(self, text: str, *, livemark=False) -> str:
        return self.filesystem.render_text(text, livemark=livemark)

    def write_text(self, path: str, *, text: str):
        return self.filesystem.write_text(path, text=text)

    # View

    def create_view(self):
        return self.filesystem.create_view()

    # TODO: fix not safe
    # TODO: remove duplication
    def write_view(self, path: str, *, view: IView):
        sa = platform.sqlalchemy
        query = view["query"]
        self.filesystem.write_view(path, view=view)
        resource = FileResource(path=path, basepath=str(self.public))
        self.database.create_record(resource=resource)

        # Get table name
        found = False
        table_names = []
        table_name = resource.name
        template = f"{table_name}%s"
        items = self.database.list_records()
        for item in items:
            name = item.get("tableName")
            if not name:
                continue
            table_names.append(name)
            if item["path"] == resource.path:
                table_name = name
                found = True
        if not found:
            suffix = 1
            while table_name in table_names:
                table_name = template % suffix
                suffix += 1

        # Create view
        with self.database.engine.begin() as conn:
            conn.execute(sa.text(f'DROP VIEW IF EXISTS "{table_name}"'))
            conn.execute(sa.text(f'CREATE VIEW "{table_name}" AS {query}'))
            conn.execute(
                sa.update(self.database.records)
                .where(self.database.records.c.path == path)
                .values(tableName=table_name)
            )
