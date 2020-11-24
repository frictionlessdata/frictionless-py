import io
from ..plugin import Plugin
from ..loader import Loader
from ..control import Control
from .. import config


# Plugin


class TextPlugin(Plugin):
    """Plugin for Text Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import TextPlugin`

    """

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "text":
            return TextControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "text":
            return TextLoader(resource)


# Control


class TextControl(Control):
    """Text control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.text import TextControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Loader


class TextLoader(Loader):
    """Text loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.text import TextLoader`

    """

    # Read

    def read_byte_stream_create(self):
        scheme = "text://"
        source = self.resource.source
        if source.startswith(scheme):
            source = source.replace(scheme, "", 1)
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(source.encode(config.DEFAULT_ENCODING))
        byte_stream.seek(0)
        return byte_stream
