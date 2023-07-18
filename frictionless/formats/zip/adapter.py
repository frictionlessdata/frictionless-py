import atexit
import json
import os
import shutil
import tempfile
from typing import Optional

from ... import errors, helpers, models
from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...resources import FileResource, TableResource
from ...system import Adapter
from .control import ZipControl

# NOTE:
# We have to move resource's zip logc to this class as well
# See `loader.read_byte_stream_decompress`
# (the same for gzip as a separate format)


class ZipAdapter(Adapter):
    def __init__(self, source: str, *, control: Optional[ZipControl] = None):
        self.source = source
        self.control = control or ZipControl()

    # Read

    def read_package(self):
        innerpath = self.control.innerpath
        resource = FileResource(path=self.source)
        resource.compression = None
        with resource:
            byte_stream = resource.byte_stream
            if resource.remote:
                byte_stream = tempfile.TemporaryFile()
                shutil.copyfileobj(resource.byte_stream, byte_stream)
                byte_stream.seek(0)
            with platform.zipfile.ZipFile(byte_stream, "r") as zip:
                tempdir = tempfile.mkdtemp()
                zip.extractall(tempdir)
                atexit.register(shutil.rmtree, tempdir)
                innerpath = innerpath or "datapackage.json"
            descriptor = os.path.join(tempdir, innerpath)
        return Package.from_descriptor(descriptor)

    # Write

    def write_package(self, package: Package):
        path = self.source
        compression = self.control.compression
        encoder_class = self.control.encoder_class

        # Save
        try:
            compression = compression or platform.zipfile.ZIP_DEFLATED
            with platform.zipfile.ZipFile(path, "w", compression=compression) as archive:
                package_descriptor = package.to_descriptor()
                for index, resource in enumerate(package.resources):
                    descriptor = package_descriptor["resources"][index]

                    # Memory data
                    if resource.memory:
                        if not isinstance(resource.data, list):
                            path = f"{resource.name}.csv"
                            descriptor.pop("data", None)
                            descriptor["path"] = path
                            descriptor["scheme"] = "file"
                            descriptor["format"] = "csv"
                            descriptor["mediatype"] = "text/csv"
                            assert isinstance(resource, TableResource)
                            with tempfile.NamedTemporaryFile() as file:
                                target = TableResource(path=file.name, format="csv")
                                resource.write(target)
                                archive.write(file.name, path)

                    # Multipart data
                    elif resource.multipart:
                        for path, normpath in zip(resource.paths, resource.normpaths):
                            if os.path.isfile(normpath):
                                if not helpers.is_safe_path(normpath):
                                    note = f'Zipping usafe "{normpath}" is not supported'
                                    error = errors.PackageError(note=note)
                                    raise FrictionlessException(error)
                                archive.write(normpath, path)

                    # Local Data
                    elif resource.normpath:
                        if resource.scheme == "file":
                            path = resource.path
                            normpath = resource.normpath
                            if os.path.isfile(normpath):
                                if not helpers.is_safe_path(normpath):
                                    note = f'Zipping usafe "{normpath}" is not supported'
                                    error = errors.PackageError(note=note)
                                    raise FrictionlessException(error)
                                archive.write(normpath, path)

                # Metadata
                archive.writestr(
                    "datapackage.json",
                    json.dumps(
                        package_descriptor,
                        indent=2,
                        ensure_ascii=False,
                        cls=encoder_class,
                    ),
                )

        # Error
        except Exception as exception:
            error = errors.PackageError(note=str(exception))
            raise FrictionlessException(error) from exception

        return models.PublishResult(context=dict(path=path))
