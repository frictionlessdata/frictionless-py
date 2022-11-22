import os
import json
import shutil
import atexit
import tempfile
from typing import Optional
from ...exception import FrictionlessException
from ...platform import platform
from ...system import Adapter
from ...resource import Resource
from ...package import Package
from ... import helpers
from ... import errors
from .control import ZipControl


# NOTE:
# We have to move resource's zip logc to this class as well
# See `loader.read_byte_stream_decompress`
# (the same for gzip as a separate format)


class ZipAdapter(Adapter):
    def __init__(self, source: str, *, control: Optional[ZipControl] = None):
        self.control = control or ZipControl()
        self.source = source

    # Read

    def read_package(self):
        innerpath = self.control.innerpath
        with Resource(path=self.source, compression=None) as resource:
            byte_stream = resource.byte_stream
            if resource.remote:
                byte_stream = tempfile.TemporaryFile()
                shutil.copyfileobj(resource.byte_stream, byte_stream)
                byte_stream.seek(0)
            with platform.zipfile.ZipFile(byte_stream, "r") as zip:
                tempdir = tempfile.mkdtemp()
                zip.extractall(tempdir)
                atexit.register(shutil.rmtree, tempdir)
                if not innerpath:
                    innerpath = "datapackage.json"
                    extensions = ("json", "yaml")
                    default_names = (f"datapackage.{ext}" for ext in extensions)
                    for name in default_names:
                        if os.path.isfile(os.path.join(tempdir, name)):
                            innerpath = name
                            break
                descriptor = os.path.join(tempdir, innerpath)
        return Package.from_descriptor(descriptor)

    # Write

    def write_package(self, package: Package):
        path = self.source
        compression = self.control.compression
        encoder_class = self.control.encoder_class

        # Infer
        package.infer(sample=False)

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
                            with tempfile.NamedTemporaryFile() as file:
                                target = Resource(path=file.name, format="csv")
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
                    elif resource.scheme == "file":
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

        return True
