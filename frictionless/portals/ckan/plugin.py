from __future__ import annotations
from ...plugin import Plugin
from .control import CkanControl
from .manager import CkanManager


# Plugin


class CkanPlugin(Plugin):
    """Plugin for CKAN"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "ckan":
            return CkanControl.from_descriptor(descriptor)

    def create_manager(self, name, source, **options):
        if name == "ckan":
            return CkanManager(source, **options)
