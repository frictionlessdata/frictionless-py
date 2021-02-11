import io
from ..plugin import Plugin
from ..loader import Loader
from ..control import Control
from .. import helpers


# Plugin


class LocalPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalPlugin`

    """

    code = "local"

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "file":
            return LocalControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "file":
            return LocalLoader(resource)


# Control


class LocalControl(Control):
    """Local control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }


# Loader


class LocalLoader(Loader):
    """Local loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalLoader`

    """

    # Read

    def read_byte_stream_create(self):
        scheme = "file://"
        fullpath = self.resource.fullpath
        if fullpath.startswith(scheme):
            fullpath = fullpath.replace(scheme, "", 1)
        byte_stream = io.open(fullpath, "rb")
        return byte_stream

    # Write

    def write_byte_stream(self, path):
        helpers.move_file(path, self.resource.fullpath)
