import os
import datetime
import secrets
import shutil
from pathlib import Path
from typing import Optional
from ..exception import FrictionlessException
from ..resource import Resource
from ..package import Package
from .database import Database
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

    def file_copy(self, source: str, target: Optional[str] = None):
        target = target or source
        source = str(self.public / source)
        target = str(self.public / target)
        if os.path.isdir(source):
            shutil.copytree(source, target)
            return
        assert os.path.isfile(source)
        target = deduplicate_path(target, suffix="copy")
        helpers.copy_file(source, target)

    # TODO: use streaming?
    def file_create(self, path: str, *, bytes: bytes):
        path = str(self.public / path)
        path = deduplicate_path(path)
        helpers.write_file(path, bytes, mode="wb")
        return path

    def file_create_folder(self, path: str):
        path = str(self.public / path)
        assert not os.path.exists(path)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def file_delete(self, path: str):
        path = str(self.public / path)
        if os.path.isdir(path):
            shutil.rmtree(path)
            return
        assert os.path.isfile(path)
        os.remove(path)

    def file_list(self, with_folders=False, only_folders=False):
        paths = []
        temp_folders = set()
        for basepath, folders, files in os.walk(self.public):
            if not only_folders:
                for file in files:
                    path = os.path.join(basepath, file)
                    path = os.path.relpath(path, start=self.public)
                    paths.append(path)
                    temp_folders.add(os.path.dirname(path))
            if with_folders or only_folders:
                for folder in folders:
                    if folder.startswith("."):
                        continue
                    path = os.path.join(basepath, folder)
                    path = os.path.relpath(path, start=self.public)
                    if path in temp_folders:
                        continue
                    paths.append(path)
        paths = list(sorted(paths))
        return paths

    def file_move(self, source: str, target: str):
        source = str(self.public / source)
        target = str(self.public / target)
        assert not os.path.exists(target)
        if os.path.isdir(source):
            shutil.move(source, target)
            return
        assert os.path.isfile(source)
        helpers.move_file(source, target)

    # TODO: use streaming?
    def file_read(self, path: str):
        path = str(self.public / path)
        assert os.path.isfile(path)
        bytes = helpers.read_file(path, "rb")
        return bytes

    # Package

    def package_create(self):
        package_path = settings.PACKAGE_PATH
        paths = self.file_list()
        if package_path not in paths:
            package = Package(basepath=self.basepath)
            for path in paths:
                try:
                    if os.path.isdir(self.public / path):
                        continue
                    record = self.resource_create(path)
                    resource = Resource.from_descriptor(record.resource)  # type: ignore
                    package.add_resource(resource)
                except FrictionlessException as exception:
                    if "already exists" in exception.error.note:
                        continue
                    raise exception
                except Exception as exception:
                    raise exception

            package.to_json(str(self.public / package_path))
        return package_path

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

    def resource_create(self, path: str):
        path = str(self.public / path)
        resource = Resource(path=path)
        record = self.database.create_resource(resource)
        return record

    def resource_delete(self, path: str):
        self.database.delete_resource(path)

    def resource_describe(self, path: str):
        pass

    def resource_extract(self, path: str):
        pass

    def resource_list(self):
        return self.database.list_resources()

    def resource_read(self, path: str):
        return self.database.read_resource(path)

    # TODO: use streaming?
    # TODO: rebase on using resource's metadata if available
    def resource_read_bytes(self, path: str):
        path = str(self.public / path)
        assert os.path.isfile(path)
        with Resource(path=path) as resource:
            bytes = resource.read_bytes()
            return bytes

    # TODO: rebase on using resource's metadata if available
    def resource_read_data(self, path: str):
        path = str(self.public / path)
        assert os.path.isfile(path)
        with Resource(path=path) as resource:
            data = resource.read_data()
            return data

    # TODO: use streaming?
    # TODO: rebase on resource's metadata or accept encoding?
    def resource_read_text(self, path: str):
        path = str(self.public / path)
        assert os.path.isfile(path)
        with Resource(path=path) as resource:
            text = resource.read_text()
            return text

    def resource_transform(self, path: str):
        pass

    def resource_update(self, path: str):
        self.database.update_resource(path)


# Internal


def deduplicate_path(path: str, *, suffix: str = ""):
    if os.path.exists(path):
        number = 1
        parts = os.path.splitext(path)
        template = f"{parts[0]} ({suffix}%s){parts[1]}"
        while os.path.exists(path):
            path = template % number
            number += 1
    return path
