import io
import os
from urllib.parse import urlparse
from ..control import Control
from ..plugin import Plugin
from ..loader import Loader
from .. import helpers


# Plugin


class S3Plugin(Plugin):
    """Plugin for S3

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.s3 import S3Plugin`

    """

    code = "s3"
    status = "experimental"

    def create_control(self, resource, *, descriptor):
        if resource.scheme == "s3":
            return S3Control(descriptor)

    def create_loader(self, resource):
        if resource.scheme == "s3":
            return S3Loader(resource)


# Control


class S3Control(Control):
    """S3 control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.s3 import S3Control`

    Parameters:
        descriptor? (str|dict): descriptor
        endpoint_url? (string): endpoint url

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, endpoint_url=None):
        self.setinitial("endpointUrl", endpoint_url)
        super().__init__(descriptor)

    @property
    def endpoint_url(self):
        return (
            self.get("endpointUrl")
            or os.environ.get("S3_ENDPOINT_URL")
            or DEFAULT_ENDPOINT_URL
        )

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("endpointUrl", self.endpoint_url)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "endpointUrl": {"type": "string"},
        },
    }


# Loader


class S3Loader(Loader):
    """S3 loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.s3 import S3Loader`

    """

    remote = True

    # Read

    def read_byte_stream_create(self):
        boto3 = helpers.import_from_plugin("boto3", plugin="s3")
        control = self.resource.control
        parts = urlparse(self.resource.fullpath, allow_fragments=False)
        client = boto3.resource("s3", endpoint_url=control.endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])
        byte_stream = S3ByteStream(object)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        boto3 = helpers.import_from_plugin("boto3", plugin="s3")
        control = self.resource.control
        parts = urlparse(self.resource.fullpath, allow_fragments=False)
        client = boto3.resource("s3", endpoint_url=control.endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])
        object.put(Body=byte_stream)


# Internal


DEFAULT_ENDPOINT_URL = "https://s3.amazonaws.com"


# https://alexwlchan.net/2019/02/working-with-large-s3-objects/
class S3ByteStream(io.RawIOBase):
    def __init__(self, object):
        self.object = object
        self.position = 0

    def __repr__(self):
        return "<%s object=%r>" % (type(self).__name__, self.object)

    @property
    def size(self):
        return self.object.content_length

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.size + offset
        else:
            raise ValueError(
                "invalid whence (%r, should be %d, %d, %d)"
                % (whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END)
            )

        return self.position

    def read(self, size=-1):
        if size == -1:
            # EOF
            if self.position >= self.size:
                return b""
            # Read to the end of the file
            range_header = "bytes=%d-" % self.position
            self.seek(offset=0, whence=io.SEEK_END)
        else:
            new_position = self.position + size
            # If we're going to read beyond the end of the object, return
            # the entire object.
            if new_position >= self.size:
                return self.read()
            range_header = "bytes=%d-%d" % (self.position, new_position - 1)
            self.seek(offset=size, whence=io.SEEK_CUR)
        return self.object.get(Range=range_header)["Body"].read()

    def read1(self, size=-1):
        return self.read(size)
