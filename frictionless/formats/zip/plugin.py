from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from ...system import Plugin
from ... import helpers
from .adapter import ZipAdapter
from .control import ZipControl

if TYPE_CHECKING:
    from ...dialect import Control


class ZipPlugin(Plugin):
    """Plugin for Zip"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if packagify:
            if isinstance(source, str):
                source = helpers.join_basepath(source, basepath=basepath)
                if helpers.is_zip_descriptor(source):
                    control = control if isinstance(control, ZipControl) else ZipControl()
                    adapter = ZipAdapter(source, control=control)
                    return adapter
