import os
import datetime
import secrets
import shutil
from pathlib import Path
from typing import Optional, Dict
from fastapi import UploadFile
from frictionless.exception import FrictionlessException
from frictionless.portals.ckan.control import CkanControl
from frictionless.portals.github.control import GithubControl
from frictionless.portals.zenodo.control import ZenodoControl
from .config import Config
from .record import Record
from ..package import Package
from ..resource import Resource
from .. import settings
from .. import helpers


# TODO: fix create/validate logic

# TODO: move to db
RECORDS: Dict[str, Record] = {}


class Project:
    session: Optional[str]
    public: Path
    private: Path

    def __init__(self, config: Config, *, session: Optional[str] = None):
        base = Path(config.basepath or "")

        # Validate session
        # TODO: raise not authorized access
        if session:
            assert not config.root
            assert os.path.isdir(base / session)

        # Create session
        elif not config.root:
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

    # Props

    @property
    def basepath(self):
        return str(self.public)

    # Project

    def read_bytes(self, path: str):
        # TODO: ensure that path is safe
        resource = Resource(path=path, basepath=self.basepath)
        bytes = resource.read_bytes()
        return bytes

    def read_text(self, path: str):
        # TODO: ensure that path is safe
        resource = Resource(path=path, basepath=self.basepath)
        text = resource.read_text()
        return text

    # Config

    # Files

    def create_file(self, file: UploadFile):
        # TODO: use streaming
        # TODO: handle errors
        # TODO: sanitize filename
        path = str(self.public / file.filename)
        body = file.file.read()
        helpers.write_file(path, body, mode="wb")
        return file.filename

    def create_directory(self, path: str):
        path = str(self.public / path)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def delete_file(self, path: str):
        # TODO: ensure that path is safe
        fullpath = self.public / path
        if os.path.isdir(fullpath):
            shutil.rmtree(fullpath)
        else:
            os.remove(fullpath)
        return path

    def list_files(self):
        paths = []
        temp_folders = set()
        for basepath, folders, files in os.walk(self.public):
            for file in files:
                path = os.path.join(basepath, file)
                path = os.path.relpath(path, start=self.public)
                paths.append(path)
                temp_folders.add(os.path.dirname(path))

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

    def list_folders(self):
        folders = []
        for basepath, names, _ in os.walk(self.public):
            for name in names:
                if name.startswith("."):
                    continue
                path = os.path.join(basepath, name)
                path = os.path.relpath(path, start=self.public)
                folders.append(path)
        folders = list(sorted(folders))
        return folders

    def move_file(self, filepath: str, destination: str):
        filename = os.path.basename(filepath)
        source = str(self.public / filepath)
        destination = str(self.public / destination)
        newpath = os.path.join(destination, filename)
        helpers.move_file(source, newpath)
        return newpath

    def copy_file(self, source: str, destination: str):
        new_filename = os.path.basename(source)
        source_fullpath = str(self.public / source)
        destination_filepath = str(self.public / destination / new_filename)
        # Set new filename if it already exists
        if os.path.exists(destination_filepath):
            while True:
                new_filename = f"copyof{new_filename}"
                destination_filepath = str(self.public / destination / new_filename)
                if not os.path.exists(destination_filepath):
                    break
        if os.path.isdir(source_fullpath):
            helpers.copy_folder(source_fullpath, destination_filepath)
        else:
            helpers.copy_file(source_fullpath, destination_filepath)
        return destination_filepath

    # Links

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
        controls = {"github": GithubControl, "zenodo": ZenodoControl, "ckan": CkanControl}
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
                type=report.task.type,
                updated=os.path.getmtime(resource.normpath),
                resource=resource.to_descriptor(),
                report=report.to_descriptor(),
            )
        record = RECORDS[path]
        return record

    def update_resord(self, resource: Resource):
        print(resource)
