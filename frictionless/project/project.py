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

    # TODO: rename
    def file_copy(self, path: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.copy_file(path, folder=folder)

    # TODO: use streaming?
    def file_create(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        return self.filesystem.create_file(name, bytes=bytes, folder=folder)

    def file_delete(self, path: str) -> str:
        return self.filesystem.delete_file(path)

    def file_list(self) -> List[IFileItem]:
        files: List[IFileItem] = []
        items = self.filesystem.list_files()
        for item in items:
            path = item["path"]
            type = "folder" if item["isFolder"] else "file"
            if item["path"] == "datapackage.json":
                type = "package"
            files.append(IFileItem(path=path, type=type))
        return files

    def file_move(self, path: str, *, folder: str) -> str:
        return self.filesystem.move_file(path, folder=folder)

    # TODO: use Resource?
    # TODO: use streaming?
    def file_read(self, path: str) -> bytes:
        return self.filesystem.read_file(path)

    def file_rename(self, path: str, *, name: str) -> str:
        return self.filesystem.rename_file(path, name=name)

    # Folder

    def folder_create(self, name: str, *, folder: Optional[str] = None) -> str:
        return self.filesystem.create_folder(name, folder=folder)

    # Package

    def package_create(self):
        path = str(self.public / settings.PACKAGE_PATH)
        if not os.path.exists(path):
            helpers.write_file(path, json.dumps({"resource": []}))
        path = str(Path(path).relative_to(self.public))
        return path

    def package_publish(self, **params):
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

    def resource_create(self, path: str) -> IRecord:
        resource = Resource(path=path, basepath=str(self.public))
        return self.database.create_resource(resource)

    def resource_delete(self, path: str) -> str:
        return self.database.delete_resource(path)

    def resource_list(self) -> List[IListedRecord]:
        return self.database.list_resources()

    def resource_query(self, query: str) -> ITable:
        return self.database.query_resources(query)

    def resource_provide(self, path: str) -> IRecord:
        record = self.resource_read(path)
        if not record:
            record = self.resource_create(path)
        return record

    def resource_read(self, path: str) -> Optional[IRecord]:
        return self.database.read_resource(path)

    # TODO: rewrite
    def resource_read_table(
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

    def resource_update(self, path: str):
        self.database.update_resource(path)


# Internal


def deduplicate_path(path: str, *, suffix: str = "") -> str:
    if os.path.exists(path):
        number = 1
        parts = os.path.splitext(path)
        template = f"{parts[0]} ({suffix}%s){parts[1]}"
        while os.path.exists(path):
            path = template % number
            number += 1
    return path


def is_hidden_path(path: str) -> bool:
    for part in os.path.split(path):
        if part.startswith(".") and len(part) > 1:
            return True
    return False
