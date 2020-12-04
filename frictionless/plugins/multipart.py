from ..loader import Loader
from ..plugin import Plugin
from ..control import Control


# Plugin


class MultipartPlugin(Plugin):
    """Plugin for Multipart Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartPlugin`

    """

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "multipart":
            return MultipartControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "multipart":
            return MultipartLoader(resource)


# Control


class MultipartControl(Control):
    """Multipart control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Loader


class MultipartLoader(Loader):
    """Multipart loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartLoader`

    """

    pass
