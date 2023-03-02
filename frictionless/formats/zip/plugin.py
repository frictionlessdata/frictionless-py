from __future__ import annotations
from ...system import Plugin
from ... import helpers
from .adapter import ZipAdapter
from .control import ZipControl


class ZipPlugin(Plugin):
    """Plugin for Zip"""

    # Hooks

    def create_adapter(self, source, *, control=None, basepath=None, packagify=False):
        if packagify:
            if isinstance(source, str):
                source = helpers.join_basepath(source, basepath=basepath)
                if helpers.is_zip_descriptor(source):
                    control = control if isinstance(control, ZipControl) else ZipControl()
                    adapter = ZipAdapter(source, control=control)
                    return adapter
