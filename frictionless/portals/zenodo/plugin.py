from __future__ import annotations
from ...plugin import Plugin
from urllib.parse import urlparse
from .control import ZenodoControl
from .manager import ZenodoManager


# Plugin


class ZenodoPlugin(Plugin):
    """Plugin for Zenodo"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "zenodo":
            return ZenodoControl.from_descriptor(descriptor)

    def create_manager(self, source, *, control=None):
        parsed = urlparse(source)
        if not control or isinstance(control, ZenodoControl):
            if parsed.netloc == "zenodo.com":
                control = control or ZenodoControl()
                user, repo = parsed.path.split("/")[1:]
                control.user = user
                if repo:
                    control.repo = repo
                return ZenodoManager(control)
