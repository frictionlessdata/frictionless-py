import io
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader
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
        text = self.resource.fullpath
        if text.startswith(scheme):
            text = text.replace(scheme, "", 1)
        if text.endswith(f".{self.resource.format}"):
            text = text[: -(len(self.resource.format) + 1)]
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(text.encode(config.DEFAULT_ENCODING))
        byte_stream.seek(0)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        bytes = byte_stream.read()
        text = bytes.decode(self.resource.encoding)
        return text
