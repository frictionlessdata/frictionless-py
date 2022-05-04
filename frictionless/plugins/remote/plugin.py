import requests
from ...plugin import Plugin
from .control import RemoteControl
from .loader import RemoteLoader
from . import settings


class RemotePlugin(Plugin):
    """Plugin for Remote Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.remote import RemotePlugin`

    """

    code = "remote"

    def create_control(self, resource, *, descriptor):
        if resource.scheme in settings.DEFAULT_SCHEMES:
            return RemoteControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme in settings.DEFAULT_SCHEMES:
            return RemoteLoader(resource)

    # Helpers

    @staticmethod
    def create_http_session():
        http_session = requests.Session()
        http_session.headers.update(settings.DEFAULT_HTTP_HEADERS)
        return http_session
