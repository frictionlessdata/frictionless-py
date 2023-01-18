import os
import datetime
import secrets
import shutil
from pathlib import Path
from typing import Optional, Dict
from ..exception import FrictionlessException
from ..resource import Resource
from ..package import Package
from .record import Record
from .. import settings
from .. import helpers
from .. import portals


# TODO: fix create/validate logic

# TODO: move to db
RECORDS: Dict[str, Record] = {}


# TODO: handle method errors?
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
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.session = session
        self.public = public
        self.private = private

    @property
    def basepath(self):
        return str(self.public)

    # Files

    def list_files(self, with_dirs=False, only_dirs=False):
        paths = []
        temp_folders = set()
        for basepath, folders, files in os.walk(self.public):
            if not only_dirs:
                for file in files:
                    path = os.path.join(basepath, file)
                    path = os.path.relpath(path, start=self.public)
                    paths.append(path)
                    temp_folders.add(os.path.dirname(path))
            if with_dirs or only_dirs:
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

    # TODO: use streaming?
    # TODO: ensure that path is safe
    def create_file(self, path: str, *, contents: bytes):
        path = str(self.public / path)
        assert not os.path.exists(path)
        helpers.write_file(path, contents, mode="wb")
        return path

    # TODO: use streaming?
    # TODO: ensure that path is safe
    def read_file(self, path: str):
        path = str(self.public / path)
        assert os.path.isfile(path)
        contents = helpers.read_file(path, mode="rb")
        return contents

    # TODO: ensure that path is safe
    def move_file(self, source: str, target: str):
        source = str(self.public / source)
        target = str(self.public / target)
        assert os.path.isfile(source)
        assert not os.path.exists(target)
        helpers.move_file(source, target)

    # TODO: ensure that path is safe
    def copy_file(self, source: str, target: Optional[str] = None):
        target = target or source
        source = str(self.public / source)
        assert os.path.isfile(source)
        target = str(self.public / target)
        # Set new filename if it already exists
        if os.path.exists(target):
            number = 1
            parts = os.path.splitext(target)
            template = f"{parts[0]} (copy%s){parts[1]}"
            while os.path.exists(target):
                target = template % number
                number += 1
        helpers.copy_file(source, target)

    # TODO: ensure that path is safe
    def delete_file(self, path: str):
        # TODO: ensure that path is safe
        path = str(self.public / path)
        assert os.path.isfile(path)
        os.remove(path)

    # TODO: ensure that path is safe
    def create_dir(self, path: str):
        path = str(self.public / path)
        assert not os.path.exists(path)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    # TODO: ensure that path is safe
    def move_dir(self, source: str, target: str):
        source = str(self.public / source)
        assert os.path.isdir(source)
        assert not os.path.exists(target)
        shutil.move(source, target)

    # TODO: ensure that path is safe
    def delete_dir(self, path: str):
        path = str(self.public / path)
        assert os.path.isdir(path)
        shutil.rmtree(path)

    # Records

    def create_record(self, path: str):
        if path not in RECORDS:
            resource = Resource(path=path, basepath=self.basepath)
            report = resource.validate()
            RECORDS[path] = Record(
                path=path,
                # TODO: deduplicate
                name=report.task.name,
                # TODO: support package/etc types?
                updated=os.path.getmtime(resource.normpath),
                resource=resource.to_descriptor(),
                report=report.to_descriptor(),
            )
        record = RECORDS[path]
        return record

    def update_record(self, resource: Resource):
        print(resource)

    # Packages

    def create_package(self):
        package_path = settings.PACKAGE_PATH
        paths = self.list_files()
        if package_path not in paths:
            package = Package(basepath=self.basepath)
            for path in paths:
                try:
                    if os.path.isdir(self.public / path):
                        continue
                    record = self.create_record(path)
                    resource = Resource.from_descriptor(record.resource)
                    package.add_resource(resource)
                except FrictionlessException as exception:
                    if "already exists" in exception.error.note:
                        continue
                    raise exception
                except Exception as exception:
                    raise exception

            package.to_json(str(self.public / package_path))
        return package_path

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
