from __future__ import annotations
from ...plugin import Plugin
from urllib.parse import urlparse
from .control import CkanControl
from .manager import CkanManager


# Plugin


class CkanPlugin(Plugin):
    """Plugin for Ckan"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "ckan":
            return CkanControl.from_descriptor(descriptor)

    # TODO: improve
    def create_manager(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, CkanControl):
                if parsed.path.startswith("/dataset/"):
                    control = control or CkanControl()
                    baseurl, dataset = source.split("/dataset/")
                    control.baseurl = baseurl
                    if dataset:
                        control.dataset = dataset
                    return CkanManager(control)