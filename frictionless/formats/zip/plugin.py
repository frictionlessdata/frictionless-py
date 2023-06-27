from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ... import helpers
from ...platform import platform
from ...system import Plugin
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
        if not isinstance(source, str):
            return
        fullpath = helpers.join_basepath(source, basepath=basepath)
        _, format = helpers.parse_scheme_and_format(fullpath)
        if format != "zip":
            return
        if not packagify:
            if helpers.is_remote_path(fullpath):
                return
            with platform.zipfile.ZipFile(fullpath, "r") as zip:
                if "datapackage.json" not in zip.namelist():
                    return
        control = control if isinstance(control, ZipControl) else ZipControl()
        adapter = ZipAdapter(fullpath, control=control)
        return adapter
