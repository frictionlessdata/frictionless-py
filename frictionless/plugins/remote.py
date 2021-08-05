import io
import requests.utils
from ..metadata import Metadata
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader
from ..system import system


# Plugin


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


# Control


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
        return self.get("httpTimeout", DEFAULT_HTTP_TIMEOUT)

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


# Loader


class RemoteLoader(Loader):
    """Remote loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.remote import RemoteLoader`

    """

    remote = True

    # Read

    def read_byte_stream_create(self):
        fullpath = requests.utils.requote_uri(self.resource.fullpath)
        session = self.resource.control.http_session
        timeout = self.resource.control.http_timeout
        byte_stream = RemoteByteStream(fullpath, session=session, timeout=timeout).open()
        if self.resource.control.http_preload:
            buffer = io.BufferedRandom(io.BytesIO())
            buffer.write(byte_stream.read())
            buffer.seek(0)
            byte_stream = buffer
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        file = f"{self.resource.name}.{self.resource.format}"
        url = self.resource.fullpath.replace(file, "")
        response = self.resource.control.http_session.post(url, files={file: byte_stream})
        response.raise_for_status()
        return response


# Internal


DEFAULT_SCHEMES = ["http", "https", "ftp", "ftps"]
DEFAULT_HTTP_TIMEOUT = 10
DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/54.0.2840.87 Safari/537.36"
    )
}


class RemoteByteStream:
    def __init__(self, source, *, session, timeout):
        self.__source = source
        self.__session = session
        self.__timeout = timeout

    def __iter__(self):
        while True:
            bytes = self.read(8192)
            if not bytes:
                break
            yield from bytes.splitlines(keepends=True)

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return True

    @property
    def closed(self):
        return self.__closed

    def open(self):
        self.__closed = False
        self.seek(0)
        return self

    def close(self):
        self.__closed = True

    def tell(self):
        return self.__response.raw.tell()

    def flush(self):
        pass

    def read(self, size=-1):
        if size == -1:
            size = None
        return self.__response.raw.read(size)

    def read1(self, size=-1):
        return self.read(size)

    def seek(self, offset, whence=0):
        assert offset == 0
        assert whence == 0
        self.__response = self.__session.get(
            self.__source, stream=True, timeout=self.__timeout
        )
        self.__response.raise_for_status()
        self.__response.raw.decode_content = True
