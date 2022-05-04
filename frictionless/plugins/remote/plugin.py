import requests
from ...plugin import Plugin
from .control import RemoteControl
from .loader import RemoteLoader


class RemotePlugin(Plugin):
    """Plugin for Remote Data

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.remote import RemotePlugin`

    """

    code = "remote"

    def create_control(self, resource, *, descriptor):
        if resource.scheme in DEFAULT_SCHEMES:
            return RemoteControl(descriptor)

    def create_loader(self, resource):
        if resource.scheme in DEFAULT_SCHEMES:
            return RemoteLoader(resource)

    # Helpers

    @staticmethod
    def create_http_session():
        http_session = requests.Session()
        http_session.headers.update(DEFAULT_HTTP_HEADERS)
        return http_session


# Internal


DEFAULT_SCHEMES = ["http", "https", "ftp", "ftps"]
DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/54.0.2840.87 Safari/537.36"
    )
}
