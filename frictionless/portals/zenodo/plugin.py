from __future__ import annotations
from ...plugin import Plugin
from urllib.parse import urlparse
from .control import ZenodoControl
from .manager import ZenodoManager


# Plugin


class ZenodoPlugin(Plugin):
    """Plugin for Zenodo"""

    # Hooks

    # TODO: improve
    def create_manager(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, ZenodoControl):
                if parsed.netloc == "zenodo.org":
                    control = control or ZenodoControl()
                    if parsed.path.startswith("/record/"):
                        control.record = parsed.path.replace("/record/", "")
                    return ZenodoManager(control)

    def select_Control(self, type):
        if type == "zenodo":
            return ZenodoControl
