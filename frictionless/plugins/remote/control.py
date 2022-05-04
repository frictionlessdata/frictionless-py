from ...metadata import Metadata
from ...control import Control
from ...system import system
from . import settings


class RemoteControl(Control):
    """Remote control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.remote import RemoteControl`

    Parameters:
        descriptor? (str|dict): descriptor
        http_session? (requests.Session): user defined HTTP session
        http_preload? (bool): don't use HTTP streaming and preload all the data
        http_timeout? (int): user defined HTTP timeout in minutes

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        http_session=None,
        http_preload=None,
        http_timeout=None,
    ):
        self.setinitial("httpSession", http_session)
        self.setinitial("httpPreload", http_preload)
        self.setinitial("httpTimeout", http_timeout)
        super().__init__(descriptor)

    @Metadata.property
    def http_session(self):
        """
        Returns:
            requests.Session: HTTP session
        """
        http_session = self.get("httpSession")
        if not http_session:
            http_session = system.get_http_session()
        return http_session

    @Metadata.property
    def http_preload(self):
        """
        Returns:
            bool: if not streaming
        """
        return self.get("httpPreload", False)

    @Metadata.property
    def http_timeout(self):
        """
        Returns:
            int: HTTP timeout in minutes
        """
        return self.get("httpTimeout", settings.DEFAULT_HTTP_TIMEOUT)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("httpPreload", self.http_preload)
        self.setdefault("httpTimeout", self.http_timeout)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "httpSession": {},
            "httpPreload": {"type": "boolean"},
            "httpTimeout": {"type": "number"},
        },
    }
