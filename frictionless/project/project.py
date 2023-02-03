import os
import json
import datetime
import secrets
import shutil
from pathlib import Path
from typing import Optional, List
from ..exception import FrictionlessException
from ..resource import Resource
from ..package import Package
from .database import Database
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

    @property
    def basepath(self):
        return str(self.public)

    # File

    def file_copy(self, path: str, *, folder: Optional[str] = None) -> str:
        name = os.path.basename(path)
        folder = folder or os.path.dirname(path)
        source = str(self.public / path)
        basetarget = str(self.public / folder)
        target = str(self.public / folder / name)
        target = deduplicate_path(target, suffix="copy")
        assert os.path.isdir(basetarget)
        # File
        if os.path.isfile(source):
            helpers.copy_file(source, target)
        # Folder
        elif os.path.isdir(source):
            helpers.copy_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = str(Path(target).relative_to(self.public))
        return path

    # TODO: use streaming?
    def file_create(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        assert not os.path.dirname(name)
        basepath = str(self.public / (folder or ""))
        path = str(self.public / (folder or "") / name)
        path = deduplicate_path(path)
        assert os.path.isdir(basepath)
        helpers.write_file(path, bytes, mode="wb")
        path = str(Path(path).relative_to(self.public))
        return path

    def file_delete(self, path: str) -> str:
        path = str(self.public / path)
        # File
        if os.path.isfile(path):
            os.remove(path)
        # Folder
        elif os.path.isdir(path):
            shutil.rmtree(path)
        # Missing
        else:
            FrictionlessException("file doesn't exist")
        path = str(Path(path).relative_to(self.public))
        return path

    def file_list(self) -> List[IFileItem]:
        items: List[IFileItem] = []
        for basepath, folders, files in os.walk(self.public):
            basepath = os.path.relpath(basepath, start=self.public)
            if basepath == ".":
                basepath = ""
            if is_hidden_path(basepath):
                continue
            for file in files:
                if file.startswith("."):
                    continue
                path = os.path.join(basepath, file)
                type = "package" if file == "datapackage.json" else "file"
                items.append({"path": path, "type": type})
            for folder in folders:
                if folder.startswith("."):
                    continue
                path = os.path.join(basepath, folder)
                items.append({"path": path, "type": "folder"})
        items = list(sorted(items, key=lambda item: f'{item["path"]}'))
        return items

    def file_list_plain(self, *, exclude_folders: bool = False) -> List[str]:
        paths = []
        for item in self.file_list():
            if exclude_folders and item["type"] == "folder":
                continue
            paths.append(item["path"])
        return paths

    def file_move(self, path: str, *, folder: str) -> str:
        name = os.path.basename(path)
        source = str(self.public / path)
        basetarget = str(self.public / folder)
        target = str(self.public / folder / name)
        target = deduplicate_path(target)
        assert os.path.isdir(basetarget)
        # File
        if os.path.isfile(source):
            helpers.move_file(source, target)
        # Folder
        elif os.path.isdir(source):
            helpers.move_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = str(Path(target).relative_to(self.public))
        return path

    # TODO: use Resource?
    # TODO: use streaming?
    def file_read(self, path: str) -> bytes:
        path = str(self.public / path)
        assert os.path.isfile(path)
        bytes = helpers.read_file(path, "rb")
        return bytes

    def file_rename(self, path: str, *, name: str) -> str:
        folder = os.path.dirname(path)
        source = str(self.public / path)
        target = str(self.public / folder / name)
        assert not os.path.exists(target)
        # File
        if os.path.isfile(source):
            helpers.move_file(source, target)
        # Folder
        elif os.path.isdir(source):
            helpers.move_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = str(Path(target).relative_to(self.public))
        return path

    # Folder

    def folder_create(self, name: str, *, folder: Optional[str] = None) -> str:
        assert not os.path.dirname(name)
        basepath = str(self.public / (folder or ""))
        path = str(self.public / (folder or "") / name)
        assert os.path.isdir(basepath)
        assert not os.path.exists(path)
        Path(path).mkdir(parents=True, exist_ok=False)
        path = str(Path(path).relative_to(self.public))
        return path

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
