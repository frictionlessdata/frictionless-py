import os
import secrets
from pathlib import Path
from typing import Optional, Dict
from fastapi import UploadFile
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
        os.remove(self.public / path)
        return path

    def list_files(self):
        paths = []
        for basepath, _, names in os.walk(self.public):
            for name in names:
                path = os.path.join(basepath, name)
                path = os.path.relpath(path, start=self.public)
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

    def move_file(self, filename: str, destination: str):
        source = str(self.public / filename)
        destination = str(self.public / destination)
        newpath = os.path.join(destination, filename)
        helpers.move_file(source, newpath)
        return newpath

    # Links

    # Packages

    def create_package(self):
        package_path = settings.PACKAGE_PATH
        paths = self.list_files()
        if package_path not in paths:
            package = Package(basepath=self.basepath)
            for path in paths:
                record = self.create_record(path)
                resource = Resource.from_descriptor(record.resource)
                package.add_resource(resource)
            package.to_json(str(self.public / package_path))
        return package_path

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
