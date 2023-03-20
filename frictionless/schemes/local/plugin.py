from __future__ import annotations
from ...system import Plugin
from .control import LocalControl
from .loader import LocalLoader
from .adapter import LocalAdapter
from ... import helpers


class LocalPlugin(Plugin):
    """Plugin for Local Data"""

    # Hooks

    def create_adapter(self, source, *, control=None, basepath=None, packagify=False):
        if source is not None:
            path = source
            if isinstance(source, str):
                path = helpers.join_basepath(source, basepath=basepath)
            if helpers.is_directory_source(path) or helpers.is_expandable_source(path):
                return LocalAdapter(source, basepath=basepath)

    def create_loader(self, resource):
        if resource.scheme == "file":
            if not helpers.is_remote_path(resource.basepath or ""):
                return LocalLoader(resource)

    def select_control_class(self, type):
        if type == "local":
            return LocalControl
