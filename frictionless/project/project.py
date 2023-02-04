from __future__ import annotations
import os
import json
import datetime
import secrets
from pathlib import Path
from typing import Optional, List
from ..exception import FrictionlessException
from ..resource import Resource
from ..package import Package
from .database import Database
from .filesystem import Filesystem
from .interfaces import IFileItem, ITable, IRecord, IListedRecord
from .. import settings
from .. import helpers
from .. import portals

# TODO: handle method errors?
# TODO: ensure that path is safe for all the methods


class Project:
    session: Optional[str]
    public: Path
    private: Path
    database: Database
    filesystem: Filesystem

    def __init__(
        self,
        *,
        session: Optional[str] = None,
        basepath: Optional[str] = None,
        is_root: bool = False,
    ):
        base = Path(basepath or "")

        # Validate session
        # TODO: raise not authorized access
        if session:
            assert not is_root
            assert os.path.isdir(base / session)

        # Create session
        elif not is_root:
            session = secrets.token_urlsafe(16)

        # Ensure project
        public = base / (session or "")
        private = public / ".frictionless"
        database = private / "project.db"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.session = session
        self.public = public
        self.private = private
        self.database = Database(f"sqlite:///{database}")
        self.filesystem = Filesystem(str(self.public))

    @property
    def basepath(self):
        return str(self.public)

    # File

    def copy_file(self, path: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.copy_file(path, folder=folder)

    # TODO: use streaming?
    def create_file(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        return self.filesystem.create_file(name, bytes=bytes, folder=folder)

    def delete_file(self, path: str) -> str:
        return self.filesystem.delete_file(path)

    def list_files(self) -> List[IFileItem]:
        files: List[IFileItem] = []
        items = self.filesystem.list_files()
        for item in items:
            path = item["path"]
            type = "folder" if item["isFolder"] else "file"
            if item["path"] == "datapackage.json":
                type = "package"
            files.append(IFileItem(path=path, type=type))
        return files

    def move_file(self, path: str, *, folder: str) -> str:
        return self.filesystem.move_file(path, folder=folder)

    # TODO: use Resource?
    # TODO: use streaming?
    def read_file(self, path: str) -> bytes:
        return self.filesystem.read_file(path)

    def rename_file(self, path: str, *, name: str) -> str:
        return self.filesystem.rename_file(path, name=name)

    # Folder

    def create_folder(self, name: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.create_folder(name, folder=folder)

    # Package

    def create_package(self):
        path = str(self.public / settings.PACKAGE_PATH)
        if not os.path.exists(path):
            helpers.write_file(path, json.dumps({"resource": []}))
        path = str(Path(path).relative_to(self.public))
        return path

    def publish_package(self, **params):
        response = {}
        controls = {
            "github": portals.GithubControl,
            "zenodo": portals.ZenodoControl,
            "ckan": portals.CkanControl,
        }
        control_type = params["type"]
        allow_update = params["allow_update"]

        del params["type"]
        del params["sandbox"]
        if not allow_update:
            del params["allow_update"]

        package = Package(str(self.public / settings.PACKAGE_PATH))
        if not package.name and not allow_update:
            now = datetime.datetime.now()
            date_time = now.strftime("%H-%M-%S")
            package.name = f"test_package_{date_time}"

        control = controls.get(control_type)
        if not control:
            response["error"] = "Matching control[Github|Zenodo|CKAN] not found"
            return response
        try:
            if "url" in params:
                target = params["url"]
                del params["url"]
                result = package.publish(target=target, control=control(**params))
            else:
                result = package.publish(control=control(**params))
            if control_type == "github":
                result = result.full_name
            response["url"] = result
        except FrictionlessException as exception:
            response["error"] = exception.error.message

        return response

    # Resource

    def create_resource(self, path: str) -> IRecord:
        resource = Resource(path=path, basepath=str(self.public))
        return self.database.create_resource(resource)

    def delete_resource(self, path: str) -> str:
        return self.database.delete_resource(path)

    def list_resources(self) -> List[IListedRecord]:
        return self.database.list_resources()

    def query_resources(self, query: str) -> ITable:
        return self.database.query_resources(query)

    def provide_resource(self, path: str) -> IRecord:
        record = self.read_resource(path)
        if not record:
            record = self.create_resource(path)
        return record

    def read_resource(self, path: str) -> Optional[IRecord]:
        return self.database.read_resource(path)

    # TODO: rewrite
    def read_resource_table(
        self,
        path: str,
        *,
        valid: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ITable:
        record = self.database.read_resource(path)
        assert record
        query = 'select * from "%s"' % record["tableName"]
        if valid is not None:
            query = "%s where _rowValid = %s" % (query, valid)
        if limit:
            query = "%s limit %s" % (query, limit)
            if offset:
                query = "%s offset %s" % (query, offset)
        table = self.database.query_resources(query)
        table["tableSchema"] = record["resource"]["schema"]
        return table

    def update_resource(self, path: str):
        self.database.update_resource(path)
