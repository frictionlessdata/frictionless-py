from __future__ import annotations
from ...system import Plugin
from ... import helpers
from .adapter import ZipAdapter
from .control import ZipControl


class ZipPlugin(Plugin):
    """Plugin for Zip"""

    # Hooks

    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            if helpers.is_zip_descriptor(source):
                control = control if isinstance(control, ZipControl) else ZipControl()
                adapter = ZipAdapter(source, control=control)
                return adapter
