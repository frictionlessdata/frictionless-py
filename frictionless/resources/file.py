from __future__ import annotations
from typing import Optional, Union
from ..resource import Resource
from .. import helpers


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
                    chunk = self.byte_stream.read1()  # type: ignore
                    buffer += chunk
                    if not chunk:
                        break
                return buffer
            return self.byte_stream.read1(size)  # type: ignore

    # Write

    # TODO: rebase on using loader
    def write_file(self, target: Optional[Union[FileResource, str]] = None, **options):
        """Write bytes to the target"""
        res = target
        if not isinstance(res, FileResource):
            if res:
                options["path"] = res
            res = FileResource(**options)
        bytes = self.read_file()
        assert res.normpath
        helpers.write_file(res.normpath, bytes, mode="wb")
        return res
