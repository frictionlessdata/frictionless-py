from __future__ import annotations
from ...system import Plugin
from urllib.parse import urlparse
from .control import CkanControl
from .adapter import CkanAdapter


class CkanPlugin(Plugin):
    """Plugin for Ckan"""

    # Hooks

    # TODO: improve
    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, CkanControl):
                if parsed.path.startswith("/dataset/"):
                    control = control or CkanControl()
                    baseurl, dataset = source.split("/dataset/")
                    control.baseurl = baseurl
                    if dataset:
                        control.dataset = dataset
                    return CkanAdapter(control)

    def select_Control(self, type):
        if type == "ckan":
            return CkanControl
