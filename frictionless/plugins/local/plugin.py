from ...plugin import Plugin
from .control import LocalControl
from .loader import LocalLoader


class LocalPlugin(Plugin):
    """Plugin for Local Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalPlugin`

    """

    code = "local"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "local":
            return LocalControl.from_descriptor(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "file":
            return LocalLoader(resource)
