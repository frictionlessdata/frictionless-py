from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Optional, Union, List, Any, Dict
from ..dialect import Control
from ..package import Package
from ..resource import Resource
from ..resources import FileResource, TextResource, JsonResource
from ..exception import FrictionlessException
from .interfaces import IFileItem, IView
from .. import helpers


# TODO: move specific logic to endpoint classes
# TODO: is it possible to move most of this functionality to resources.FileResource?
class Filesystem:
    basepath: Path

    def __init__(self, basepath: str):
        # We need to get resolve here to get absolute path
        self.basepath = Path(basepath).resolve()

    # Chart

    def create_chart(self):
        path = self.get_secure_fullpath("chart.json", deduplicate=True)
        self.write_json(path, data={"encoding": {}})
        path = self.get_secure_relpath(path)
        return path

    # File

    def copy_file(self, path: str, *, folder: Optional[str] = None) -> str:
        name = self.get_filename(path)
        if folder:
            folder = self.get_secure_fullpath(folder)
            assert self.is_folder(folder)
        source = self.get_secure_fullpath(path)
        target = self.get_secure_fullpath(folder, name, deduplicate="copy")
        # File
        if self.is_file(source):
            helpers.copy_file(source, target)
        # Folder
        elif self.is_folder(source):
            helpers.copy_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = self.get_secure_relpath(target)
        return path

    # TODO: use streaming?
    def create_file(
        self, name: str, *, bytes: bytes, folder: Optional[str] = None
    ) -> str:
        assert self.is_filename(name)
        if folder:
            folder = self.get_secure_fullpath(folder)
            assert self.is_folder(folder)
        path = self.get_secure_fullpath(folder, name, deduplicate=True)
        helpers.write_file(path, bytes, mode="wb")
        path = self.get_secure_relpath(path)
        return path

    def delete_file(self, path: str) -> str:
        path = self.get_secure_fullpath(path)
        # File
        if self.is_file(path):
            os.remove(path)
        # Folder
        elif self.is_folder(path):
            shutil.rmtree(path)
        # Missing
        else:
            FrictionlessException("file doesn't exist")
        path = self.get_secure_relpath(path)
        return path

    def list_files(self) -> List[IFileItem]:
        items: List[IFileItem] = []
        for root, folders, files in os.walk(self.basepath):
            if not self.is_basepath(root):
                folder = self.get_secure_relpath(root)
                if self.is_hidden_path(folder):
                    continue
            for file in files:
                if self.is_hidden_path(file):
                    continue
                type = self.get_filetype(os.path.join(root, file))
                path = self.get_secure_relpath(os.path.join(root, file))
                item = IFileItem(path=path)
                if type:
                    item["type"] = type
                items.append(item)
            for folder in folders:
                if self.is_hidden_path(folder):
                    continue
                path = self.get_secure_relpath(os.path.join(root, folder))
                items.append(IFileItem(path=path, type="folder"))
        items = list(sorted(items, key=lambda item: item["path"]))
        return items

    def select_file(self, path: str) -> Optional[IFileItem]:
        path = self.get_secure_fullpath(path)
        if self.is_existent(path):
            type = self.get_filetype(path)
            if self.is_folder(path):
                type = "folder"
            path = self.get_secure_relpath(path)
            file = IFileItem(path=path)
            if type:
                file["type"] = type
            return file

    def move_file(self, path: str, *, folder: Optional[str] = None) -> str:
        name = self.get_filename(path)
        if folder:
            folder = self.get_secure_fullpath(folder)
            assert self.is_folder(folder)
        source = self.get_secure_fullpath(path)
        target = self.get_secure_fullpath(folder, name, deduplicate=True)
        # File
        if self.is_file(source):
            helpers.move_file(source, target)
        # Folder
        elif self.is_folder(source):
            helpers.move_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = self.get_secure_relpath(target)
        return path

    def read_file(self, path: str) -> bytes:
        path = self.get_secure_fullpath(path)
        assert self.is_file(path)
        resource = FileResource(path=path)
        return resource.read_file()

    def rename_file(self, path: str, *, name: str) -> str:
        folder = self.get_folder(path)
        if folder:
            folder = self.get_secure_fullpath(folder)
            assert self.is_folder(folder)
        source = self.get_secure_fullpath(path)
        target = self.get_secure_fullpath(folder, name, deduplicate="renamed")
        # File
        if self.is_file(source):
            helpers.move_file(source, target)
        # Folder
        elif self.is_folder(source):
            helpers.move_folder(source, target)
        # Missing
        else:
            raise FrictionlessException("file doesn't exist")
        path = self.get_secure_relpath(target)
        return path

    def write_file(self, path: str, *, bytes: bytes) -> None:
        path = self.get_secure_fullpath(path)
        resource = FileResource(data=bytes)
        resource.write_file(path)

    # Folder

    def create_folder(self, name: str, *, folder: Optional[str] = None) -> str:
        assert self.is_filename(name)
        if folder:
            folder = self.get_secure_fullpath(folder)
            assert self.is_folder(folder)
        path = self.get_secure_fullpath(folder, name, deduplicate=True)
        helpers.create_folder(path)
        path = self.get_secure_relpath(path)
        return path

    # Json

    def read_json(self, path: str) -> Any:
        path = self.get_secure_fullpath(path)
        resource = JsonResource(path=path)
        return resource.read_json()

    def write_json(self, path: str, *, data: Any):
        path = self.get_secure_fullpath(path)
        resource = JsonResource(data=data)
        resource.write_json(path=path)

    # Package

    def create_package(self):
        path = self.get_secure_fullpath("datapackage.json", deduplicate=True)
        self.write_json(path, data={"resources": []})
        path = self.get_secure_relpath(path)
        return path

    def publish_package(self, path: str, *, control: Dict[str, Any]) -> str:
        path = self.get_secure_fullpath(path)
        package = Package.from_descriptor(path)
        return package.publish(control=Control.from_descriptor(control))

    # Text

    # TODO: use detected resource.encoding if indexed
    def read_text(self, path: str) -> str:
        path = self.get_secure_fullpath(path)
        resource = TextResource(path=path)
        return resource.read_text()

    def render_text(self, path: str, livemark: bool = False) -> str:
        path = self.get_secure_fullpath(path)
        resource = TextResource(path=path)
        return resource.render_text(livemark=livemark)

    def write_text(self, path: str, *, text: str):
        path = self.get_secure_fullpath(path)
        resource = TextResource(data=text)
        resource.write_text(path=path)

    # View

    def create_view(self):
        path = self.get_secure_fullpath("view.json", deduplicate=True)
        self.write_json(path, data={"query": ""})
        path = self.get_secure_relpath(path)
        return path

    def write_view(self, path: str, *, view: IView):
        path = self.get_secure_fullpath(path)
        # TODO: use ViewResource?
        resource = JsonResource(data=view)
        resource.write_json(path=path)

    # Helpers

    def get_secure_fullpath(
        self, *paths: Optional[str], deduplicate: Union[bool, str] = False
    ) -> str:
        # We need to use resolve here to get normalized path
        fullpath = str(self.basepath.joinpath(*filter(None, paths)).resolve())
        assert self.get_secure_relpath(fullpath)
        if deduplicate:
            suffix = deduplicate if isinstance(deduplicate, str) else ""
            fullpath = self.deduplicate_fullpath(fullpath, suffix=suffix)
        return fullpath

    def get_secure_relpath(self, fullpath: str) -> str:
        # We need to use resolve here to prevent path traversing
        path = str(Path(fullpath).resolve().relative_to(self.basepath))
        assert path != "."
        assert path != ""
        return path

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
        return self.basepath.samefile(path)

    def is_existent(self, fullpath: str) -> bool:
        return os.path.exists(fullpath)

    def is_filename(self, name: str) -> bool:
        return not os.path.dirname(name)

    def is_folder(self, fullpath: str) -> bool:
        return os.path.isdir(fullpath)

    def is_file(self, fullpath: str) -> bool:
        return os.path.isfile(fullpath)

    def deduplicate_fullpath(self, fullpath: str, *, suffix: str = "") -> str:
        if os.path.exists(fullpath):
            number = 1
            parts = os.path.splitext(fullpath)
            template = f"{parts[0]} ({suffix}%s){parts[1]}"
            while os.path.exists(fullpath):
                fullpath = template % number
                number += 1
        return fullpath
