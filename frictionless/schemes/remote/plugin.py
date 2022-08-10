from __future__ import annotations
from ...plugin import Plugin
from ...platform import platform
from .control import RemoteControl
from .loader import RemoteLoader
from . import settings


class RemotePlugin(Plugin):
    """Plugin for Remote Data"""

    # Hooks

    def create_loader(self, resource):
        if resource.scheme in settings.DEFAULT_SCHEMES:
            return RemoteLoader(resource)

    def select_Control(self, type):
        if type == "remote":
            return RemoteControl

    # Helpers

    @staticmethod
    def create_http_session():
        http_session = platform.requests.Session()
        http_session.headers.update(settings.DEFAULT_HTTP_HEADERS)
        return http_session
