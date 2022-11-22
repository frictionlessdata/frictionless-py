from __future__ import annotations
from ...system import Plugin
from urllib.parse import urlparse
from .control import ZenodoControl
from .adapter import ZenodoAdapter


class ZenodoPlugin(Plugin):
    """Plugin for Zenodo"""

    # Hooks

    # TODO: improve
    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, ZenodoControl):
                if parsed.netloc == "zenodo.org":
                    control = control or ZenodoControl()
                    if parsed.path.startswith("/record/"):
                        control.record = parsed.path.replace("/record/", "")
                    if parsed.path.startswith("/deposit/"):
                        control.deposition_id = int(parsed.path.replace("/deposit/", ""))
                    return ZenodoAdapter(control)

        if not source and isinstance(control, ZenodoControl):
            return ZenodoAdapter(control=control)

    def select_Control(self, type):
        if type == "zenodo":
            return ZenodoControl
