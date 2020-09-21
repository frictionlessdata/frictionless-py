import requests
from .metadata import Metadata
from . import helpers
from . import errors
from . import config


class Control(Metadata):
    """Control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import controls`

    Parameters:
        descriptor? (str|dict): descriptor
        detectEncoding? (func):  a function to detect encoding `(sample) -> encoding`

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, detect_encoding=None):
        self.setinitial("detectEncoding", detect_encoding)
        super().__init__(descriptor)

    @Metadata.property
    def detect_encoding(self):
        """
        Returns:
            func: detect encoding function
        """
        return self.get("detectEncoding", helpers.detect_encoding)

    # Expand

    def expand(self):
        pass

    # Import/Export

    def to_dict(self, expand=False):
        result = super().to_dict()
        if expand:
            result = type(self)(result)
            result.expand()
            result = result.to_dict()
        return result

    # Metadata

    metadata_Error = errors.ControlError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {"detectEncoding": {}},
    }


class LocalControl(Control):
    """Local control representation

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {"detectEncoding": {}},
    }


class RemoteControl(Control):
    """Remote control representation

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
        detect_encoding=None,
    ):
        self.setinitial("httpSession", http_session)
        self.setinitial("httpPreload", http_preload)
        self.setinitial("httpTimeout", http_timeout)
        super().__init__(descriptor, detect_encoding=detect_encoding)

    @Metadata.property
    def http_session(self):
        """
        Returns:
            requests.Session: HTTP session
        """
        http_session = self.get("httpSession")
        if not http_session:
            http_session = requests.Session()
            http_session.headers.update(config.DEFAULT_HTTP_HEADERS)
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
        return self.get("httpTimeout", config.DEFAULT_HTTP_TIMEOUT)

    # Expand

    def expand(self):
        """Expand metadata"""
        super().expand()
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
            "detectEncoding": {},
        },
    }


class StreamControl(Control):
    """Stream control representation

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {"detectEncoding": {}},
    }


class TextControl(Control):
    """Text control representation

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {"detectEncoding": {}},
    }
