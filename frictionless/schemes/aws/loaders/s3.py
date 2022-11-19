from __future__ import annotations
import io
from urllib.parse import urlparse
from ..control import AwsControl
from ....system import Loader
from ....platform import platform


class S3Loader(Loader):
    """S3 loader implementation."""

    remote = True

    # Read

    def read_byte_stream_create(self):
        control = AwsControl.from_dialect(self.resource.dialect)
        parts = urlparse(self.resource.normpath, allow_fragments=False)
        client = platform.boto3.resource("s3", endpoint_url=control.s3_endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])  # type: ignore
        byte_stream = S3ByteStream(object)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        control = AwsControl.from_dialect(self.resource.dialect)
        parts = urlparse(self.resource.normpath, allow_fragments=False)
        client = platform.boto3.resource("s3", endpoint_url=control.s3_endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])  # type: ignore
        object.put(Body=byte_stream)


# Internal


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
