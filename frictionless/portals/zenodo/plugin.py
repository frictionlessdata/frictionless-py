from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlparse

from ...system import Plugin
from .adapter import ZenodoAdapter
from .control import ZenodoControl

if TYPE_CHECKING:
    from ...dialect import Control


class ZenodoPlugin(Plugin):
    """Plugin for Zenodo"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
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
        if source is None and isinstance(control, ZenodoControl):
            return ZenodoAdapter(control=control)

    def select_control_class(self, type: Optional[str] = None):
        if type == "zenodo":
            return ZenodoControl
