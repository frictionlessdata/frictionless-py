from ..plugin import Plugin
from ..loader import Loader
from ..control import Control
from ..exception import FrictionlessException
from .. import errors


# Plugin


class FilelikePlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.filelike import FilelikePlugin`

    """

    def create_file(self, file):
        if not file.scheme and not file.format:
            if hasattr(file.data, "read"):
                file.scheme = "filelike"
                file.format = ""
                return file

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "filelike":
            return FilelikeControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "filelike":
            return FilelikeLoader(resource)


# Control


class FilelikeControl(Control):
    """Filelike control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.filelike import FilelikeControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Loader


class FilelikeLoader(Loader):
    """Filelike loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.filelike import FilelikeLoader`

    """

    # Read

    def read_byte_stream_create(self):
        data = self.resource.data
        if hasattr(data, "encoding"):
            error = errors.SchemeError(note="only byte streams are supported")
            raise FrictionlessException(error)
        return data

    # Write

    def write_byte_stream_save(self, byte_stream):
        return byte_stream
