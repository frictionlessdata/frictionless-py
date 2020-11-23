from ..plugin import Plugin
from ..loader import Loader
from ..control import Control
from .. import exceptions
from .. import errors


# Plugin


class StreamPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamPlugin`

    """

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "stream":
            return StreamControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "stream":
            return StreamLoader(resource)


# Control


class StreamControl(Control):
    """Stream control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Loader


class StreamLoader(Loader):
    """Stream loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamLoader`

    """

    # Read

    def read_byte_stream_create(self):
        source = self.resource.source
        if hasattr(source, "encoding"):
            error = errors.SchemeError(note="only byte streams are supported")
            raise exceptions.FrictionlessException(error)
        return source
