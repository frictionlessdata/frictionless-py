from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlparse

from ...system import Plugin
from .adapter import CkanAdapter
from .control import CkanControl

if TYPE_CHECKING:
    from ...dialect import Control


class CkanPlugin(Plugin):
    """Plugin for Ckan"""

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
            if not control or isinstance(control, CkanControl):
                if re.search(r"^/dataset/[^/]+$", parsed.path):
                    control = control or CkanControl()
                    if not control.baseurl:
                        baseurl, dataset = source.split("/dataset/")
                        control.baseurl = baseurl
                    else:
                        dataset = source.split("/dataset/")[1]
                    if dataset:
                        control.dataset = dataset
                elif control:
                    control.dataset = source

                if isinstance(control, CkanControl):
                    return CkanAdapter(control)
        if source is None and isinstance(control, CkanControl):
            return CkanAdapter(control)

    def select_control_class(self, type: Optional[str] = None):
        if type == "ckan":
            return CkanControl
