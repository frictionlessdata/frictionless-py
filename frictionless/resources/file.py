from __future__ import annotations

from typing import Any, Optional, Union, cast

from .. import helpers
from ..exception import FrictionlessException
from ..resource import Resource


class FileResource(Resource):
    type = "file"
    datatype = "file"

    # Read

    # TODO: rebase on using loader
    def read_file(self, *, size: Optional[int] = None) -> bytes:
        """Read bytes into memory

        Returns:
            any[][]: resource bytes
        """
        if self.memory:
            if isinstance(self.data, bytes):
                return self.data
        with helpers.ensure_open(self):
            # Without size we need to read chunk by chunk because read1 doesn't return
            # the full contents by default (just an arbitrary amount of bytes)
            # and we use read1 as it includes stats calculation (system.loader)
            if not size:
                buffer = b""
                while True:
                    chunk = cast(bytes, self.byte_stream.read1())  # type: ignore
                    buffer += chunk
                    if not chunk:
                        break
                return buffer
            return self.byte_stream.read1(size)  # type: ignore

    # Write

    # TODO: rebase on using loader
    def write_file(
        self, target: Optional[Union[FileResource, str]] = None, **options: Any
    ):
        """Write bytes to the target"""
        resource = target
        if not isinstance(resource, Resource):
            resource = FileResource(**options)
        if not isinstance(resource, FileResource):  # type: ignore
            raise FrictionlessException("target must be a text resource")
        bytes = self.read_file()
        assert resource.normpath
        helpers.write_file(resource.normpath, bytes, mode="wb")
        return resource


class ImageResource(FileResource):
    datatype = "image"


class DocumentResource(FileResource):
    datatype = "document"
