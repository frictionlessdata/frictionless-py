import io
from ..plugin import Plugin
from ..loader import Loader
from ..control import Control


# Plugin


class LocalPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalPlugin`

    """

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

    pass


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
        source = self.resource.source
        if source.startswith(scheme):
            source = source.replace(scheme, "", 1)
        byte_stream = io.open(source, "rb")
        return byte_stream
